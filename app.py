"""SkinSense Explainer - plain-language layer over the SkinSense classifier.

Pipeline: classifier label -> retrieve reference entry -> LLM rewrite grounded
in that entry -> validate -> show, or fall back to deterministic text.
Styling is shared with the SkinSense Space via brand.py.
"""
import gradio as gr
import brand
import guard
import llm
import retrieve

DISCLAIMER = (
    "Educational screening aid, not a medical device. It does not diagnose, treat or cure "
    "any condition. Always consult a qualified dermatologist about a skin concern."
)

SKINSENSE_URL = "https://elisha622-skinsense.hf.space"

# Labels the SkinSense classifier actually emits (config.CLASSES), mapped to the
# reference entries this app holds. Classes with no reference entry are handled
# explicitly rather than silently falling through to "unknown".
NO_ENTRY = {
    "dry_skin": "Dry skin",
    "hyperpigmentation": "Hyperpigmentation",
    "normal_skin": "Normal skin",
    "oily_skin": "Oily skin",
    "rosacea": "Rosacea",
}

# Geist is loaded in HEAD_HTML, which does not block first paint. Naming it here
# stops Gradio fetching its own font from Google and waiting on it before drawing.
THEME = gr.themes.Default(font=brand.FONT_STACK).set(
    body_background_fill=brand.PAGE,
    block_background_fill=brand.CARD,
    block_border_color=brand.LINE,
    block_label_text_color=brand.SUBTLE,
    body_text_color=brand.INK,
    button_primary_background_fill=brand.FOREST,
    button_primary_background_fill_hover=brand.PINE,
    button_primary_text_color=brand.WHITE,
)


def _trace(kind, detail=""):
    """Validation outcome as a chip, matching SkinSense's status styling."""
    label = {"ok": "Passed validation",
             "fallback": "Fallback served",
             "refused": "Refused"}[kind]
    dot = {"ok": "&check;", "fallback": "!", "refused": "&times;"}[kind]
    html = (f'<div class="ss-panel ss-card"><p class="ss-kicker">Validation</p>'
            f'<span class="ss-chip ss-chip-{kind}">{dot} {label}</span>')
    if detail:
        html += f'<div class="ss-chip-detail">{detail}</div>'
    return html + "</div>"


def explain(label, confidence, question):
    if label in NO_ENTRY:
        return (f"SkinSense can classify {NO_ENTRY[label]}, but this Explainer has no reference "
                f"entry for it yet, so there is nothing grounded to say. Adding one means adding "
                f"it to data/conditions.json.", _trace("refused", "no reference entry"))

    entry = retrieve.by_label(label)
    if entry is None:
        return f"'{label}' is not a known label.", _trace("refused", "unknown label")

    source = retrieve.entry_text(entry)
    text = llm.explain(entry["name"], llm.band(confidence), source, question.strip())

    if text is None:
        return (guard.fallback(entry, confidence) + "\n\n" + DISCLAIMER,
                _trace("fallback", "no model output (no API key, or the call failed)"))

    ok, reasons = guard.validate(text, source)
    if not ok:
        return (guard.fallback(entry, confidence) + "\n\n" + DISCLAIMER,
                _trace("fallback", "; ".join(reasons)))
    return text + "\n\n" + DISCLAIMER, _trace("ok")


def followup(question):
    hits = retrieve.search(question)
    if not hits:
        return ("That question is outside the reference set, so it will not be answered from the "
                "model's own memory.", _trace("refused", "no retrieval match above floor"))
    key, entry, score = hits[0]
    source = retrieve.entry_text(entry)
    text = llm.explain(entry["name"], "n/a", source, question)
    if text is None:
        return (f"{entry['name']}: {entry['what_it_is']}\n\n{DISCLAIMER}",
                _trace("fallback", f"no model output; matched {entry['name']} at {score:.2f}"))
    ok, reasons = guard.validate(text, source)
    if not ok:
        return (f"{entry['name']}: {entry['what_it_is']}\n\n{DISCLAIMER}",
                _trace("fallback", "; ".join(reasons)))
    return f"{text}\n\n{DISCLAIMER}", _trace("ok", f"matched {entry['name']} at {score:.2f}")


with gr.Blocks(title="SkinSense Explainer") as demo:
    gr.HTML(
        '<div id="ss-header">' + brand.wordmark(42, "hdr", light=True, sub="Explainer") +
        '<div class="ss-tag">Turns a SkinSense result into plain language, grounded in a curated '
        'reference. Every response is checked for treatment advice, definitive diagnoses and '
        'ungrounded claims before it is shown. &nbsp;·&nbsp; '
        '<a href="' + SKINSENSE_URL + '" style="color:#E6C9A3;text-decoration:underline;">'
        'Open SkinSense</a></div></div>'
    )

    GUIDE = (
        '<div class="ss-panel ss-card ss-reveal" style="margin-top:15px;">'
        '<p class="ss-kicker">How this is kept honest</p>'
        '<div style="display:flex;flex-direction:column;gap:9px;">'
        '<span style="font-size:0.79rem;color:' + brand.SUBTLE + ';display:flex;gap:9px;">'
        '<b style="color:' + brand.EMERALD + ';">&check;</b> Answers come only from the curated reference, never the model\'s own memory</span>'
        '<span style="font-size:0.79rem;color:' + brand.SUBTLE + ';display:flex;gap:9px;">'
        '<b style="color:' + brand.EMERALD + ';">&check;</b> Treatment advice and definitive diagnoses are blocked before display</span>'
        '<span style="font-size:0.79rem;color:' + brand.SUBTLE + ';display:flex;gap:9px;">'
        '<b style="color:' + brand.EMERALD + ';">&check;</b> Sentences not grounded in the source trigger the deterministic fallback</span>'
        '<span style="font-size:0.79rem;color:' + brand.SUBTLE + ';display:flex;gap:9px;">'
        '<b style="color:' + brand.EMERALD + ';">&check;</b> Questions outside the reference are refused rather than guessed at</span>'
        '</div></div>'
    )

    with gr.Tab("Explain a result"):
        with gr.Row():
            with gr.Column(scale=1):
                label = gr.Dropdown(
                    sorted(set(list(retrieve.CONDITIONS) + list(NO_ENTRY))),
                    value="eczema", label="Condition from SkinSense")
                conf = gr.Slider(0.0, 1.0, value=0.78, step=0.01, label="Model confidence")
                q = gr.Textbox(label="Optional question", lines=2,
                               placeholder="e.g. why does it keep coming back?")
                go = gr.Button("Explain", variant="primary")
                gr.HTML(GUIDE)
            with gr.Column(scale=2):
                out = gr.Textbox(label="Explanation", lines=12, elem_classes=["ss-card"])
                why = gr.HTML()
        go.click(fn=None, js=brand.SHOW_LOADER_JS)
        ev = go.click(explain, [label, conf, q], [out, why])
        ev.success(fn=None, js=brand.HIDE_LOADER_JS)
        ev.failure(fn=None, js=brand.HIDE_LOADER_JS)

    with gr.Tab("Ask a question"):
        fq = gr.Textbox(label="Question", lines=2,
                        placeholder="e.g. what are itchy weals that disappear within hours?")
        fgo = gr.Button("Ask", variant="primary")
        fout = gr.Textbox(label="Answer", lines=10, elem_classes=["ss-card"])
        fwhy = gr.HTML()
        fgo.click(fn=None, js=brand.SHOW_LOADER_JS)
        fev = fgo.click(followup, fq, [fout, fwhy])
        fev.success(fn=None, js=brand.HIDE_LOADER_JS)
        fev.failure(fn=None, js=brand.HIDE_LOADER_JS)

    gr.HTML('<div id="ss-note"><div class="ss-mark">' + brand.wordmark(30, "foot") + '</div>'
            '<p>Educational screening only - SkinSense is not a medical device and does not '
            'diagnose, treat or cure any condition. Always consult a qualified dermatologist '
            'about a skin concern, and seek care promptly if your skin is painful, bleeding, '
            'spreading or changing rapidly.</p></div>')

    demo.load(fn=None, js=brand.FORCE_LIGHT_JS)
    demo.load(fn=None, js=brand.REVEAL_JS)

if __name__ == "__main__":
    # Gradio 6 takes theme and css at launch time, not on Blocks.
    demo.launch(theme=THEME, css=brand.CSS, head=brand.HEAD_HTML,
                favicon_path="favicon.svg")

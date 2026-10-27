"""SkinSense Explainer - plain-language layer over the SkinSense classifier.

Pipeline: classifier label -> retrieve reference entry -> LLM rewrite grounded
in that entry -> validate -> show, or fall back to deterministic text.
"""
import gradio as gr
import guard
import llm
import retrieve

DISCLAIMER = (
    "Automated likeness check, not a diagnosis. "
    "It cannot see your history and can be wrong. Speak to a clinician about any skin concern."
)


def explain(label, confidence, question):
    entry = retrieve.by_label(label)
    if entry is None:
        return f"'{label}' is not in the reference set.", "no retrieval"

    source = retrieve.entry_text(entry)
    text = llm.explain(entry["name"], llm.band(confidence), source, question.strip())

    if text is None:
        return guard.fallback(entry, confidence) + "\n\n" + DISCLAIMER, "fallback (no model output)"

    ok, reasons = guard.validate(text, source)
    if not ok:
        return (guard.fallback(entry, confidence) + "\n\n" + DISCLAIMER,
                "fallback (validation failed: " + "; ".join(reasons) + ")")
    return text + "\n\n" + DISCLAIMER, "model output passed validation"


def followup(question):
    hits = retrieve.search(question)
    if not hits:
        return "That question is outside the reference set, so I am not going to answer it."
    key, entry, score = hits[0]
    source = retrieve.entry_text(entry)
    text = llm.explain(entry["name"], "n/a", source, question)
    if text is None:
        return f"{entry['name']}: {entry['what_it_is']}\n\n{DISCLAIMER}"
    ok, _ = guard.validate(text, source)
    body = text if ok else f"{entry['name']}: {entry['what_it_is']}"
    return f"{body}\n\n(matched: {entry['name']}, score {score:.2f})\n\n{DISCLAIMER}"


with gr.Blocks(title="SkinSense Explainer") as demo:
    gr.Markdown("# SkinSense Explainer\n"
                "Turns a SkinSense prediction into plain language, grounded in a "
                "curated reference. Every response is checked before it is shown.")
    with gr.Tab("Explain a prediction"):
        label = gr.Dropdown(sorted(retrieve.CONDITIONS), value="eczema", label="Predicted condition")
        conf = gr.Slider(0.0, 1.0, value=0.78, step=0.01, label="Model confidence")
        q = gr.Textbox(label="Optional question", placeholder="e.g. why does it keep coming back?")
        out = gr.Textbox(label="Explanation", lines=10)
        why = gr.Textbox(label="Validation trace", lines=2)
        gr.Button("Explain", variant="primary").click(explain, [label, conf, q], [out, why])
    with gr.Tab("Ask a question"):
        fq = gr.Textbox(label="Question", placeholder="e.g. what are itchy weals that disappear in hours?")
        fout = gr.Textbox(label="Answer", lines=10)
        gr.Button("Ask", variant="primary").click(followup, fq, fout)

if __name__ == "__main__":
    demo.launch()

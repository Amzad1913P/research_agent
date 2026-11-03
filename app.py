"""Gradio web interface for the deep research agent."""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import gradio as gr

from src.config import config
from src.graph import run_research
from src.utils.exports import ReportExporter

logger = logging.getLogger(__name__)
PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs"


def _safe_filename(topic: str) -> str:
    """Create a short, filesystem-safe report filename from a topic."""
    name = re.sub(r"[^\w -]", "_", topic, flags=re.UNICODE).strip(" _-")
    return (name[:50].strip() or "research_report")


def _save_report(topic: str, report: str) -> tuple[str, str, str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = OUTPUT_DIR / f"{_safe_filename(topic)}_{timestamp}"
    exporter = ReportExporter()
    markdown_path = exporter.export(report, base_path.with_suffix(".md"), "markdown")
    html_path = exporter.export(report, base_path.with_suffix(".html"), "html")
    text_path = exporter.export(report, base_path.with_suffix(".txt"), "txt")
    return str(markdown_path), str(html_path), str(text_path)


async def research(topic: str, progress: gr.Progress = gr.Progress()):
    """Run a research job and return its report, summary, and export files."""
    topic = (topic or "").strip()
    if not topic:
        return "", "Enter a research topic to begin.", None, None, None

    try:
        config.validate_config()
    except ValueError as exc:
        return "", f"Configuration error: {exc}", None, None, None

    progress(0, desc="Starting research")
    try:
        # Gradio supports async event handlers, so the graph can be awaited here.
        state: dict[str, Any] = await run_research(
            topic,
            verbose=False,
            use_cache=True,
            use_checkpoints=True,
        )
        if state.get("error"):
            return "", f"Research failed: {state['error']}", None, None, None

        report = state.get("final_report") or ""
        if not report:
            return "", "The research workflow finished without producing a report.", None, None, None

        progress(0.95, desc="Saving report files")
        markdown_path, html_path, text_path = _save_report(topic, report)
        source_count = len(state.get("search_results", []))
        finding_count = len(state.get("key_findings", []))
        section_count = len(state.get("report_sections", []))
        llm_calls = state.get("llm_calls", 0)
        tokens = state.get("total_input_tokens", 0) + state.get("total_output_tokens", 0)
        summary = (
            f"Research complete · {source_count} search results · "
            f"{finding_count} findings · {section_count} report sections · "
            f"{llm_calls} model calls · {tokens:,} estimated tokens"
        )
        progress(1, desc="Complete")
        return report, summary, markdown_path, html_path, text_path
    except Exception:
        logger.exception("Research run failed")
        return "", "The research run failed. Check the server terminal for details.", None, None, None


def build_demo() -> gr.Blocks:
    """Build the Gradio application."""
    with gr.Blocks(title="Self Learning Research Agent", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# Self Learning Research Agent\n"
            "Plan a topic, research web sources, evaluate evidence, and create a cited report."
        )
        with gr.Row():
            topic = gr.Textbox(
                label="Research topic",
                placeholder="For example: How are heat pumps changing residential energy use?",
                lines=3,
                scale=5,
            )
            run_button = gr.Button("Start research", variant="primary", scale=1)

        status = gr.Markdown("Enter a topic and start research. A run may take several minutes.")
        report = gr.Markdown(label="Research report")

        gr.Markdown("## Download report")
        with gr.Row():
            markdown_file = gr.File(label="Markdown")
            html_file = gr.File(label="HTML")
            text_file = gr.File(label="Plain text")

        run_button.click(
            fn=research,
            inputs=topic,
            outputs=[report, status, markdown_file, html_file, text_file],
            show_progress="full",
        )
        topic.submit(
            fn=research,
            inputs=topic,
            outputs=[report, status, markdown_file, html_file, text_file],
            show_progress="full",
        )

    return demo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_demo().queue().launch(
        server_name="127.0.0.1",
        server_port=7860,
        allowed_paths=[str(OUTPUT_DIR)],
    )

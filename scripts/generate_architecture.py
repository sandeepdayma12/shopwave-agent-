#!/usr/bin/env python3
"""Writes architecture.png (1-page style) for hackathon deliverable."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "architecture.png"


def main() -> None:
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(
        "ShopWave — Autonomous Support Agent (LangGraph)",
        fontsize=14,
        fontweight="bold",
        pad=12,
    )

    def box(x, y, w, h, text, fc="#e8f4fc"):
        p = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.15",
            linewidth=1.2,
            edgecolor="#1a5276",
            facecolor=fc,
        )
        ax.add_patch(p)
        ax.text(
            x + w / 2,
            y + h / 2,
            text,
            ha="center",
            va="center",
            fontsize=8.5,
            wrap=True,
        )

    def arrow(x1, y1, x2, y2):
        ax.add_patch(
            FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1,
                color="#2c3e50",
            )
        )

    box(0.3, 8.5, 2.2, 1.0, "Ingest\nPOST /process_all\n20 tickets")
    box(3.0, 8.5, 2.4, 1.0, "Concurrency\nasyncio.gather\nper ticket graph")
    box(5.8, 8.5, 2.0, 1.0, "Audit + DLQ\nlog_audit()\nfailures queued")
    box(8.2, 8.5, 1.5, 1.0, "Output\ntrace + JSON")

    box(3.5, 6.2, 3.0, 1.0, "LLM node\ncall_model\nconfidence", fc="#fef9e7")
    box(3.5, 4.5, 3.0, 1.0, "Router\n≥3 tools?\nelse nudge", fc="#fef9e7")
    box(1.0, 2.8, 2.5, 1.0, "Tool node\ncall_tools\nretries / errors", fc="#eafaf1")
    box(6.5, 2.8, 2.5, 1.0, "Nudge node\nmin tool chain\n(HumanMessage)", fc="#fdebd0")

    box(0.3, 0.5, 9.4, 1.6, "Tools: get_customer, get_order, search_knowledge_base, get_product,\ncheck_refund_eligibility (gate), issue_refund, send_reply, escalate\nMocks: random TimeoutError / malformed JSON — graph continues with tool error text", fc="#f4ecf7")

    arrow(1.4, 8.5, 4.2, 9.0)
    arrow(4.2, 8.5, 6.8, 9.0)
    arrow(6.8, 8.5, 8.5, 9.0)

    arrow(5.0, 7.2, 5.0, 6.2)
    arrow(5.0, 6.2, 5.0, 5.5)
    arrow(4.2, 4.5, 2.25, 3.8)
    arrow(5.8, 4.5, 7.75, 3.8)
    arrow(2.25, 2.8, 4.5, 5.5)
    arrow(7.75, 2.8, 5.5, 5.5)

    fig.text(
        0.5,
        0.02,
        "State: messages (reducer), ticket_id, confidence  |  Stack: FastAPI, LangGraph, OpenRouter LLM, Streamlit UI",
        ha="center",
        fontsize=8,
        style="italic",
    )

    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

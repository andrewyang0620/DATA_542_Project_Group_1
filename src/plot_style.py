import matplotlib.pyplot as plt

def set_academic_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.dpi': 300,
        'axes.spines.top': False,
        'axes.spines.right': False,
    })

COLORS = {
    "Copilot": "#0072B2",
    "GitHub Copilot": "#0072B2",
    "Codex": "#D55E00",
    "OpenAI_Codex": "#D55E00",
    "Devin": "#009E73",
    "Cursor": "#785EF0",
    "Claude Code": "#CC79A7",
    "Claude_Code": "#CC79A7",
}

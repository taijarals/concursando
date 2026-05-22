"""Application constants."""

# Menu options
MENU_OPTIONS = [
    "Dashboard",
    "Cadastros",
    "Resolver Questões",
    "Listar Questões",
    "Configurações"
]

# Difficulty levels
DIFFICULTY_LEVELS = {
    "easy": {"label": "Fácil", "icon": "🟢", "points": 10},
    "medium": {"label": "Médio", "icon": "🟡", "points": 20},
    "hard": {"label": "Difícil", "icon": "🔴", "points": 30}
}

# Badge requirements
BADGES = {
    "iniciante": {"questions": 10, "icon": "🌱"},
    "aprendiz": {"questions": 50, "icon": "📚"},
    "experiente": {"questions": 100, "icon": "⭐"},
    "mestre": {"questions": 500, "icon": "👑"},
    "perfeito": {"accuracy": 95, "icon": "💯"}
}

# Colors
COLOR_PRIMARY = "#6366F1"
COLOR_SECONDARY = "#EC4899"
COLOR_SUCCESS = "#10B981"
COLOR_DANGER = "#EF4444"
COLOR_WARNING = "#F59E0B"

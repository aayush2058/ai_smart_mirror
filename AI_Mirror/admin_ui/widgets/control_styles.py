from pathlib import Path


def application_control_styles():
    arrow = (Path(__file__).resolve().parents[2] / "assets" / "icons" / "chevron_down.svg").as_posix()
    return f"""
        QComboBox {{
            min-height: 34px; font-size: 16px; color: white; background: #263441;
            border: 1px solid #52687a; border-radius: 9px; padding: 5px 38px 5px 11px;
        }}
        QComboBox:hover {{ border-color: #72a7d3; background: #2b3b49; }}
        QComboBox:focus {{ border: 2px solid #4fa3e3; padding-left: 10px; }}
        QComboBox:disabled {{ color: #76838e; background: #1b242c; border-color: #34414b; }}
        QComboBox::drop-down {{
            subcontrol-origin: padding; subcontrol-position: top right; width: 34px;
            border: none; background: transparent;
            border-top-right-radius: 8px; border-bottom-right-radius: 8px;
        }}
        QComboBox::down-arrow {{ image: url("{arrow}"); width: 13px; height: 8px; }}
        QComboBox QAbstractItemView {{
            color: white; background: #263441; border: 1px solid #52687a;
            border-radius: 8px; padding: 5px; selection-background-color: #267fbd;
            outline: none;
        }}
        QPushButton#clearButton {{
            min-width: 88px; min-height: 40px; padding: 0 16px; font-size: 15px;
            font-weight: 600; color: #e8f0f6; background: #334453;
            border: 1px solid #607789; border-radius: 9px;
        }}
        QPushButton#clearButton:hover {{ background: #40586b; border-color: #83a9c5; }}
        QPushButton#clearButton:pressed {{ background: #273744; }}
    """

import csv
import os

import pygame

from ai.search_result import SearchResult
from ai.solver_interface import ALGORITHMS, solve
from core.constants import BG_COLOR, BORDER_COLOR, PANEL_COLOR, TEXT_COLOR, TEXT_MUTED
from core.rules import BoardRules
from ui.components.button import Button
from ui.components.titlebar import TITLEBAR_H
from ui.components.toast import Toast
from ui.screen_manager import ScreenBase


class ReportScreen(ScreenBase):
    """Compare every registered algorithm for the selected level."""

    def __init__(self, app):
        super().__init__(app)
        self.difficulty = "starter"
        self.level_id = "starter_01"
        self.level_meta = None
        self.initial_state = None
        self.rules = BoardRules()
        self.results = {}
        self.toast = Toast(self.app.fonts["body"])
        self.setup_ui()

    def setup_ui(self):
        font_body = self.app.fonts["body_bold"]
        font_btn  = self.app.fonts["button"]
        W = self.app.width
        H = self.app.height
        button_y = H - 65
        # Các nút được đặt theo tỷ lệ chiều rộng màn hình
        self.btn_menu = Button(
            rect=(50, button_y, 160, 45), text="< MENU CHÍNH", font=font_body,
            callback=lambda: self.app.switch_to_screen("main_menu"), color=(120, 115, 105),
        )
        self.btn_levels = Button(
            rect=(230, button_y, 160, 45), text="CHỌN LEVEL", font=font_body,
            callback=lambda: self.app.switch_to_screen("level_select", mode="report"), color=(79, 110, 138),
        )
        self.btn_run_all = Button(
            rect=(W - 380, button_y, 170, 45), text="CHẠY TẤT CẢ", font=font_btn,
            callback=self.run_all_algorithms, color=(46, 125, 50),
        )
        self.btn_export = Button(
            rect=(W - 195, button_y, 170, 45), text="XUẤT FILE CSV", font=font_btn,
            callback=self.export_csv_report, color=(139, 115, 85),
        )
        self.btn_export.is_enabled = False

    def _pending_results(self):
        return {
            name: SearchResult(name, False, extra={"report_status": "pending"})
            for name in ALGORITHMS
        }

    def on_enter(self, **kwargs):
        self.difficulty = kwargs.get("difficulty", "starter")
        self.level_id = kwargs.get("level_id", "starter_01")
        self.level_meta, self.initial_state = self.app.level_manager.load_level(self.difficulty, self.level_id)
        self.results = self._pending_results()
        self.btn_export.is_enabled = False
        self.toast.show("Báo cáo luôn hiển thị đầy đủ thuật toán. Bấm CHẠY TẤT CẢ để đo.")

    def run_all_algorithms(self):
        self.toast.show("Đang đo hiệu năng toàn bộ thuật toán...")
        self.results = self._pending_results()
        for name in ALGORITHMS:
            try:
                result = solve(name, self.initial_state, self.rules, max_nodes=20000, max_seconds=2.0)
                result.extra["report_status"] = "done"
                self.results[name] = result
            except Exception as exc:
                self.results[name] = SearchResult(
                    name, False, extra={"report_status": "error", "error": str(exc)}
                )
        self.btn_export.is_enabled = True
        self.toast.show(f"Đã đo đủ {len(ALGORITHMS)} thuật toán.")

    def export_csv_report(self):
        if not self.results:
            return
        out_dir = os.path.join(self.app.project_dir, "results")
        os.makedirs(out_dir, exist_ok=True)
        csv_path = os.path.join(out_dir, "algorithm_results.csv")
        try:
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Level", "Algorithm", "Status", "Solved", "Steps",
                    "Visited", "Generated", "Time (s)", "Details",
                ])
                for name in ALGORITHMS:
                    result = self.results[name]
                    status = result.extra.get("report_status", "done")
                    writer.writerow([
                        self.level_meta["name"], name, status,
                        "Yes" if result.solved else "No",
                        len(result.path) if result.solved else "N/A",
                        result.visited_count, result.generated_count,
                        f"{result.elapsed_time:.6f}",
                        result.extra.get("error", ""),
                    ])
            self.toast.show("Đã xuất đầy đủ báo cáo: results/algorithm_results.csv")
        except Exception as exc:
            self.toast.show(f"Lỗi khi xuất CSV: {exc}")

    def handle_event(self, event):
        self.btn_menu.handle_event(event)
        self.btn_levels.handle_event(event)
        self.btn_run_all.handle_event(event)
        self.btn_export.handle_event(event)

    def update(self, dt):
        self.toast.update(dt)

    def _status(self, result):
        report_status = result.extra.get("report_status", "done")
        if report_status == "pending":
            return "CHỜ CHẠY", TEXT_MUTED
        if report_status == "error":
            return "LỖI", (211, 47, 47)
        if result.solved:
            return "CÓ", (46, 125, 50)
        return "KHÔNG", (211, 47, 47)

    def draw(self, surface):
        surface.fill(BG_COLOR)
        W, H = self.app.width, self.app.height
        top = TITLEBAR_H
        title_font  = self.app.fonts["title"]
        body_font   = self.app.fonts["body"]
        body_bold   = self.app.fonts["body_bold"]
        body_small  = self.app.fonts["body_small"]

        level_name = self.level_meta["name"] if self.level_meta else "-"
        surface.blit(title_font.render(f"BÁO CÁO HIỆU NĂNG - MÀN: {level_name}", True, TEXT_COLOR),
                     (50, top + 12))
        surface.blit(body_font.render(
            f"Đầy đủ {len(ALGORITHMS)} thuật toán | Mỗi thuật toán được bảo vệ giới hạn RAM và thời gian.",
            True, TEXT_MUTED,
        ), (52, top + 48))

        # Bảng kết quả — tỷ lệ theo chiều rộng
        margin_x  = 50
        panel_w   = W - 2 * margin_x
        panel_top = top + 78
        row_h     = max(18, min(26, (H - panel_top - 245) // max(1, len(ALGORITHMS) + 1)))
        panel_h   = row_h * (len(ALGORITHMS) + 1) + 45
        panel_rect = pygame.Rect(margin_x, panel_top, panel_w, panel_h)
        pygame.draw.rect(surface, PANEL_COLOR, panel_rect, border_radius=14)
        pygame.draw.rect(surface, BORDER_COLOR, panel_rect, width=2, border_radius=14)

        # Cột header — chia đều theo panel_w
        col_pcts = [0.06, 0.24, 0.40, 0.52, 0.64, 0.79]
        col_xs   = [margin_x + int(p * panel_w) for p in col_pcts]
        headers  = ["#", "THUẬT TOÁN", "KẾT QUẢ", "SỐ BƯỚC", "ĐÃ DUYỆT", "THỜI GIAN (MS)"]
        hdr_y = panel_top + 12
        for x, header in zip(col_xs, headers):
            surface.blit(body_bold.render(header, True, (139, 115, 85)), (x, hdr_y))
        pygame.draw.line(surface, BORDER_COLOR,
                         (margin_x + 10, hdr_y + row_h),
                         (margin_x + panel_w - 10, hdr_y + row_h), 2)

        for index, name in enumerate(ALGORITHMS):
            result = self.results.get(name) or self._pending_results()[name]
            row_y = hdr_y + row_h + 4 + index * row_h
            if index % 2:
                pygame.draw.rect(surface, (250, 248, 244),
                                 (margin_x + 8, row_y - 2, panel_w - 16, row_h), border_radius=5)
            status, status_color = self._status(result)
            values = [
                (str(index + 1),                                     body_small, TEXT_MUTED),
                (name,                                               body_bold,  TEXT_COLOR),
                (status,                                             body_bold,  status_color),
                (str(len(result.path)) if result.solved else "-",   body_font,  TEXT_COLOR),
                (f"{result.visited_count:,}",                        body_font,  TEXT_COLOR),
                (f"{result.elapsed_time * 1000:.3f}",               body_font,  TEXT_COLOR),
            ]
            for x, (value, font, color) in zip(col_xs, values):
                surface.blit(font.render(value, True, color), (x, row_y))

        # Biểu đồ thanh
        chart_top = panel_top + panel_h + 14
        chart_h   = max(90, H - chart_top - 95)
        chart_rect = pygame.Rect(margin_x, chart_top, panel_w, chart_h)
        pygame.draw.rect(surface, PANEL_COLOR, chart_rect, border_radius=14)
        pygame.draw.rect(surface, BORDER_COLOR, chart_rect, width=2, border_radius=14)
        surface.blit(body_bold.render("SO SÁNH SỐ NÚT ĐÃ DUYỆT - ĐỦ TOÀN BỘ THUẬT TOÁN", True, TEXT_COLOR),
                     (margin_x + 20, chart_top + 12))

        max_visited = max(1, max((r.visited_count for r in self.results.values()), default=1))
        n_algo      = len(ALGORITHMS)
        bar_area_w  = panel_w - 40
        spacing     = bar_area_w // max(1, n_algo)
        bar_max_h   = chart_h - 60
        bar_bottom  = chart_top + chart_h - 26

        for index, name in enumerate(ALGORITHMS):
            result = self.results.get(name) or self._pending_results()[name]
            x      = margin_x + 20 + index * spacing
            bar_h  = max(3, int(result.visited_count / max_visited * bar_max_h))
            status = result.extra.get("report_status", "done")
            color  = (190, 190, 190) if status == "pending" else \
                     ((70, 160, 95) if result.solved else (210, 92, 75))
            bar_w  = max(20, spacing - 14)
            pygame.draw.rect(surface, color,
                             (x, bar_bottom - bar_h, bar_w, bar_h), border_radius=5)
            label = (
                name.replace("Simulated ", "Sim. ")
                .replace("Hill Climbing", "Hill")
                .replace("Local Beam", "Beam")
                .replace("Backtracking", "BT")
                .replace("Expectimax", "Expect.")
                .replace("AND-OR Search", "AND-OR")
                .replace("Belief-State", "Belief")
                .replace("Online Search", "Online")
            )
            text = body_small.render(label, True, TEXT_COLOR)
            surface.blit(text, text.get_rect(centerx=x + bar_w // 2, y=bar_bottom + 4))

        self.btn_menu.draw(surface)
        self.btn_levels.draw(surface)
        self.btn_run_all.draw(surface)
        self.btn_export.draw(surface)
        self.toast.draw(surface)

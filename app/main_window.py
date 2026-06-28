from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from PySide6 import QtWidgets
from sqlalchemy.orm import Session

from app.models import ReimbursementRecord, SessionLocal, init_db


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Reimbursement Simulator")
        self.resize(1200, 800)

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.tab_import = QtWidgets.QWidget(self)
        self.tab_group = QtWidgets.QWidget(self)
        self.tab_analysis = QtWidgets.QWidget(self)
        self.tab_widget.addTab(self.tab_import, "Import")
        self.tab_widget.addTab(self.tab_group, "Group")
        self.tab_widget.addTab(self.tab_analysis, "Analysis")

        self._build_import_tab()
        self._build_group_tab()
        self._build_analysis_tab()

        init_db()
        self._populate_group_combo()

    def _build_import_tab(self) -> None:
        layout = QtWidgets.QVBoxLayout(self.tab_import)

        toolbar = QtWidgets.QHBoxLayout()
        self.file_button = QtWidgets.QPushButton("파일 선택")
        self.file_button.clicked.connect(self.load_excel_or_csv)
        toolbar.addWidget(self.file_button)

        self.info_label = QtWidgets.QLabel("엑셀/CSV 파일을 불러와서 미리보기를 확인하세요.")
        toolbar.addWidget(self.info_label)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QtWidgets.QTableWidget(0, 0)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.table, 2)

        controls = QtWidgets.QHBoxLayout()
        self.start_row_edit = QtWidgets.QLineEdit()
        self.start_row_edit.setPlaceholderText("시작 row")
        self.end_row_edit = QtWidgets.QLineEdit()
        self.end_row_edit.setPlaceholderText("끝 row")
        self.delete_button = QtWidgets.QPushButton("[삭제]")
        self.delete_button.clicked.connect(self.delete_rows)
        self.save_button = QtWidgets.QPushButton("[저장]")
        self.save_button.clicked.connect(self.save_to_db)

        controls.addWidget(self.start_row_edit)
        controls.addWidget(self.end_row_edit)
        controls.addWidget(self.delete_button)
        controls.addWidget(self.save_button)
        layout.addLayout(controls)

        self.current_frame: pd.DataFrame | None = None

    def _build_group_tab(self) -> None:
        layout = QtWidgets.QVBoxLayout(self.tab_group)
        layout.addWidget(QtWidgets.QLabel("DB에 저장된 데이터의 그룹 설정을 관리할 수 있는 화면입니다."))

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(QtWidgets.QLabel("그룹 선택"))
        self.group_combo = QtWidgets.QComboBox()
        self.group_combo.addItems(["미지정", "그룹 A", "그룹 B", "그룹 C"])
        self.group_combo.currentTextChanged.connect(self.refresh_group_view)
        controls.addWidget(self.group_combo)
        self.load_group_data_button = QtWidgets.QPushButton("DB 불러오기")
        self.load_group_data_button.clicked.connect(self.refresh_group_view)
        controls.addWidget(self.load_group_data_button)
        layout.addLayout(controls)

        self.group_table = QtWidgets.QTableWidget(0, 0)
        layout.addWidget(self.group_table, 1)

        self.group_preview = QtWidgets.QPlainTextEdit()
        self.group_preview.setReadOnly(True)
        layout.addWidget(self.group_preview, 1)

    def _build_analysis_tab(self) -> None:
        layout = QtWidgets.QVBoxLayout(self.tab_analysis)
        layout.addWidget(QtWidgets.QLabel("추후 분석 기능을 위한 자리입니다."))

    def load_excel_or_csv(self) -> None:
        default_dir = str(Path(__file__).resolve().parents[1])
        sample_file = Path(default_dir) / "suga_2026.xlsx"
        if sample_file.exists():
            default_dir = str(sample_file.parent)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "파일 선택",
            default_dir,
            "Excel/CSV Files (*.xlsx *.xls *.csv)",
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(".csv"):
                frame = pd.read_csv(file_path)
            else:
                frame = pd.read_excel(file_path)
            self.current_frame = frame.copy()
            self.display_frame(self.current_frame)
            self.info_label.setText(f"불러온 파일: {file_path}")
        except Exception as exc:  # pragma: no cover - UI error path
            QtWidgets.QMessageBox.critical(self, "오류", f"파일을 읽는 중 문제가 발생했습니다.\n{exc}")

    def display_frame(self, frame: pd.DataFrame) -> None:
        self.table.setRowCount(0)
        self.table.setColumnCount(len(frame.columns))
        self.table.setHorizontalHeaderLabels([str(col) for col in frame.columns])
        self.table.verticalHeader().setVisible(True)

        for row_idx, row in frame.iterrows():
            self.table.insertRow(row_idx)
            for col_idx, value in enumerate(row.tolist()):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()

    def delete_rows(self) -> None:
        if self.current_frame is None:
            return

        selected_rows = sorted({index.row() for index in self.table.selectionModel().selectedRows()}, reverse=True)
        if selected_rows:
            self.current_frame = self.current_frame.drop(index=selected_rows).reset_index(drop=True)
            self.display_frame(self.current_frame)
            return

        try:
            start = int(self.start_row_edit.text()) if self.start_row_edit.text().strip() else 1
            end = int(self.end_row_edit.text()) if self.end_row_edit.text().strip() else len(self.current_frame)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "시작 row와 끝 row를 숫자로 입력하세요.")
            return

        if start > end:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "시작 row는 끝 row보다 작거나 같아야 합니다.")
            return

        if start < 1 or end > len(self.current_frame):
            QtWidgets.QMessageBox.warning(self, "입력 오류", "row 범위가 데이터 범위를 벗어났습니다.")
            return

        self.current_frame = self.current_frame.drop(index=list(range(start - 1, end))).reset_index(drop=True)
        self.display_frame(self.current_frame)

    def save_to_db(self) -> None:
        if self.current_frame is None:
            QtWidgets.QMessageBox.information(self, "저장", "먼저 파일을 불러오세요.")
            return

        session: Session = SessionLocal()
        try:
            for _, row in self.current_frame.iterrows():
                record = ReimbursementRecord(
                    item_code=self._safe_value(row, "item_code"),
                    item_name=self._safe_value(row, "item_name"),
                    category_code=self._safe_value(row, "category_code"),
                    department=self._safe_value(row, "department"),
                    expense_type=self._safe_value(row, "expense_type"),
                    period_1_2=self._safe_value(row, "period_1_2"),
                    payment_method=self._safe_value(row, "payment_method"),
                    business_trip=self._safe_value(row, "business_trip"),
                    travel_expense=self._safe_value(row, "travel_expense"),
                    meal_expense=self._safe_value(row, "meal_expense"),
                    lodging_expense=self._safe_value(row, "lodging_expense"),
                    remarks=self._safe_value(row, "remarks"),
                    note=self._safe_value(row, "note"),
                    group_name=self.group_combo.currentText(),
                )
                session.add(record)
            session.commit()
            QtWidgets.QMessageBox.information(self, "저장 완료", "데이터가 데이터베이스에 저장되었습니다.")
            self.refresh_group_view()
        except Exception as exc:  # pragma: no cover - UI error path
            session.rollback()
            QtWidgets.QMessageBox.critical(self, "저장 실패", f"저장 중 오류가 발생했습니다.\n{exc}")
        finally:
            session.close()

    def _safe_value(self, row: Any, column_name: str) -> str | None:
        aliases = {
            "item_code": ["item_code", "품목코드", "품목코드번호", "코드"],
            "item_name": ["item_name", "품목명", "항목명", "품목"],
            "category_code": ["category_code", "분류코드", "카테고리코드", "분류"],
            "department": ["department", "부서", "소속", "부서명"],
            "expense_type": ["expense_type", "지출유형", "비용구분", "유형"],
            "period_1_2": ["period_1_2", "1_2기", "1_2분기", "기간"],
            "payment_method": ["payment_method", "지불방식", "결제수단", "결제방식"],
            "business_trip": ["business_trip", "출장여부", "출장", "출장유무"],
            "travel_expense": ["travel_expense", "여비", "교통비", "출장비"],
            "meal_expense": ["meal_expense", "식비", "식대"],
            "lodging_expense": ["lodging_expense", "숙박비", "숙박"],
            "remarks": ["remarks", "비고", "특이사항", "메모"],
            "note": ["note", "참고", "노트", "기타"],
        }
        for alias in aliases.get(column_name, [column_name]):
            if alias in row.index:
                value = row[alias]
                if value is None or pd.isna(value):
                    return None
                return str(value)
        return None

    def _populate_group_combo(self) -> None:
        session: Session = SessionLocal()
        try:
            records = session.query(ReimbursementRecord.group_name).distinct().all()
            values = [record[0] for record in records if record[0]]
            for value in values:
                if self.group_combo.findText(value) == -1:
                    self.group_combo.addItem(value)
        finally:
            session.close()

    def refresh_group_view(self) -> None:
        session: Session = SessionLocal()
        try:
            selected_group = self.group_combo.currentText()
            records = session.query(ReimbursementRecord).filter(ReimbursementRecord.group_name == selected_group).all()
            self.group_table.setRowCount(len(records))
            self.group_table.setColumnCount(5)
            self.group_table.setHorizontalHeaderLabels(["ID", "그룹", "부서", "항목", "비고"])
            preview_lines: list[str] = []
            for row_idx, record in enumerate(records):
                self.group_table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(record.id)))
                self.group_table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(record.group_name or ""))
                self.group_table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(record.department or ""))
                self.group_table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(record.item_name or ""))
                self.group_table.setItem(row_idx, 4, QtWidgets.QTableWidgetItem(record.remarks or ""))
                preview_lines.append(f"[{record.id}] {record.item_name or '-'} / {record.department or '-'}")
            self.group_preview.setPlainText("\n".join(preview_lines) if preview_lines else "표시할 데이터가 없습니다.")
        finally:
            session.close()


def main() -> None:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

    def _build_group_tab(self) -> None:
        layout = QtWidgets.QVBoxLayout(self.tab_group)
        layout.addWidget(QtWidgets.QLabel("DB에 저장된 데이터의 그룹 설정을 관리할 수 있는 화면입니다."))
        self.group_table = QtWidgets.QTableWidget(0, 0)
        layout.addWidget(self.group_table, 1)
        self.load_group_data_button = QtWidgets.QPushButton("DB 불러오기")
        self.load_group_data_button.clicked.connect(self.load_group_data)
        layout.addWidget(self.load_group_data_button)

    def _build_analysis_tab(self) -> None:
        layout = QtWidgets.QVBoxLayout(self.tab_analysis)
        layout.addWidget(QtWidgets.QLabel("추후 분석 기능을 위한 자리입니다."))

    def load_excel_or_csv(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "파일 선택",
            str(Path.cwd()),
            "Excel/CSV Files (*.xlsx *.xls *.csv)",
        )
        if not file_path:
            return

        try:
            if file_path.lower().endswith(".csv"):
                frame = pd.read_csv(file_path)
            else:
                frame = pd.read_excel(file_path)
            self.current_frame = frame
            self.display_frame(frame)
            self.info_label.setText(f"불러온 파일: {file_path}")
        except Exception as exc:  # pragma: no cover - UI error path
            QtWidgets.QMessageBox.critical(self, "오류", f"파일을 읽는 중 문제가 발생했습니다.\n{exc}")

    def display_frame(self, frame: pd.DataFrame) -> None:
        self.table.setRowCount(len(frame))
        self.table.setColumnCount(len(frame.columns))
        self.table.setHorizontalHeaderLabels([str(col) for col in frame.columns])
        self.table.verticalHeader().setVisible(True)

        for row_idx, row in frame.iterrows():
            for col_idx, value in enumerate(row.tolist()):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()

    def delete_rows(self) -> None:
        if self.current_frame is None:
            return

        try:
            start = int(self.start_row_edit.text())
            end = int(self.end_row_edit.text())
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "시작 row와 끝 row를 숫자로 입력하세요.")
            return

        if start > end:
            QtWidgets.QMessageBox.warning(self, "입력 오류", "시작 row는 끝 row보다 작거나 같아야 합니다.")
            return

        if start < 0 or end >= len(self.current_frame):
            QtWidgets.QMessageBox.warning(self, "입력 오류", "row 범위가 데이터 범위를 벗어났습니다.")
            return

        self.current_frame = self.current_frame.drop(index=list(range(start, end + 1))).reset_index(drop=True)
        self.display_frame(self.current_frame)

    def save_to_db(self) -> None:
        if self.current_frame is None:
            QtWidgets.QMessageBox.information(self, "저장", "먼저 파일을 불러오세요.")
            return

        session: Session = SessionLocal()
        try:
            for _, row in self.current_frame.iterrows():
                record = ReimbursementRecord(
                    item_code=self._safe_value(row, "item_code"),
                    item_name=self._safe_value(row, "item_name"),
                    category_code=self._safe_value(row, "category_code"),
                    department=self._safe_value(row, "department"),
                    expense_type=self._safe_value(row, "expense_type"),
                    period_1_2=self._safe_value(row, "period_1_2"),
                    payment_method=self._safe_value(row, "payment_method"),
                    business_trip=self._safe_value(row, "business_trip"),
                    travel_expense=self._safe_value(row, "travel_expense"),
                    meal_expense=self._safe_value(row, "meal_expense"),
                    lodging_expense=self._safe_value(row, "lodging_expense"),
                    remarks=self._safe_value(row, "remarks"),
                    note=self._safe_value(row, "note"),
                )
                session.add(record)
            session.commit()
            QtWidgets.QMessageBox.information(self, "저장 완료", "데이터가 데이터베이스에 저장되었습니다.")
        except Exception as exc:  # pragma: no cover - UI error path
            session.rollback()
            QtWidgets.QMessageBox.critical(self, "저장 실패", f"저장 중 오류가 발생했습니다.\n{exc}")
        finally:
            session.close()

    def _safe_value(self, row: Any, column_name: str) -> str | None:
        value = row.get(column_name)
        if value is None or pd.isna(value):
            return None
        return str(value)

    def load_group_data(self) -> None:
        session: Session = SessionLocal()
        try:
            records = session.query(ReimbursementRecord).all()
            self.group_table.setRowCount(len(records))
            self.group_table.setColumnCount(4)
            self.group_table.setHorizontalHeaderLabels(["ID", "부서", "항목", "비고"])
            for row_idx, record in enumerate(records):
                self.group_table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(record.id)))
                self.group_table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(record.department or ""))
                self.group_table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(record.item_name or ""))
                self.group_table.setItem(row_idx, 3, QtWidgets.QTableWidgetItem(record.remarks or ""))
        finally:
            session.close()


def main() -> None:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()

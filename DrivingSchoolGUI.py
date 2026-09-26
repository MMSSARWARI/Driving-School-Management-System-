# =============================================================
#  DRIVING SCHOOL MANAGEMENT SYSTEM  –  v5
#  Fixes: layout stability on resize, sidebar shows all items,
#         students page shows package + exam info, packages page
#         shows available packages only when assigning to student,
#         selection highlight readable, no layout reordering.
# =============================================================
from importlib import import_module

# Load Qt dynamically so editors that do not have PyQt6 type stubs installed
# do not report a false unresolved-import error for the wildcard import.
try:
    _qt_widgets = import_module("PyQt6.QtWidgets")
    _qt_core = import_module("PyQt6.QtCore")
    _qt_gui = import_module("PyQt6.QtGui")
except ModuleNotFoundError as exc:
    raise ImportError(
        "PyQt6 is required. Install it with: python -m pip install PyQt6"
    ) from exc

globals().update({k: v for k, v in vars(_qt_widgets).items()
                  if not k.startswith("__")})
globals().update({name: getattr(_qt_core, name)
                  for name in ("Qt", "QDate", "QTimer", "pyqtSignal", "QSize")})
globals().update({name: getattr(_qt_gui, name)
                  for name in ("QFont", "QColor", "QPalette", "QIcon")})
import sys
try:
    import db_config   # connection settings: config.ini or defaults
except ModuleNotFoundError as exc:
    raise ImportError(
        f"Missing package '{exc.name}'. Install everything with: "
        "python -m pip install -r requirements.txt"
    ) from exc

# ─────────────────────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────────────────────
_db = None

def get_db():
    global _db
    try:
        if _db:
            _db.ping(reconnect=True, attempts=3, delay=1)
            return _db
    except Exception:
        pass
    # autocommit=True: plain reads never leave a transaction (and table
    # locks) open, so the database can be rebuilt while the app is running.
    # Writes run inside an explicit transaction - see begin().
    _db = db_config.connect(autocommit=True)
    return _db

def qry(sql, params=()):
    db  = get_db()
    cur = db.cursor()
    cur.execute(sql, params)
    return cur

def begin():
    db = get_db()
    if not db.in_transaction:
        db.start_transaction()

def commit():   get_db().commit()
def rollback(): get_db().rollback()

# ─────────────────────────────────────────────────────────────
#  PALETTE / COLOURS
# ─────────────────────────────────────────────────────────────
BG          = "#F0F4F8"
CARD        = "#FFFFFF"
BORDER      = "#DDE3ED"
TEXT        = "#111827"
MUTED       = "#6B7280"
BLUE        = "#2563EB"
BLUE_DK     = "#1D4ED8"
BLUE_LT     = "#DBEAFE"
GREEN       = "#16A34A"
GREEN_LT    = "#DCFCE7"
RED         = "#DC2626"
RED_LT      = "#FEE2E2"
AMBER       = "#D97706"
AMBER_LT    = "#FEF3C7"
PURPLE      = "#7C3AED"
SIDEBAR     = "#1E293B"
SIDEBAR_SEL = "#2563EB"
SIDEBAR_HVR = "#334155"
ROW_ALT     = "#F8FAFC"
SEL_BG      = "#DBEAFE"   # readable selection tint
SEL_FG      = "#1E3A8A"

# ─────────────────────────────────────────────────────────────
#  GLOBAL STYLESHEET
# ─────────────────────────────────────────────────────────────
APP_QSS = f"""
/* ── base ── */
* {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; }}

QMainWindow, QWidget {{ background: {BG}; color: {TEXT}; }}
QDialog              {{ background: {BG}; color: {TEXT}; }}

/* ── cards / panels ── */
QFrame#card  {{ background:{CARD}; border:1px solid {BORDER}; border-radius:14px; }}
QFrame#panel {{ background:{CARD}; border:1px solid {BORDER}; border-radius:10px; }}

/* ── inputs ── */
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background:white; border:1.5px solid {BORDER}; border-radius:8px;
    padding:6px 10px; color:{TEXT};
    selection-background-color:{BLUE_LT}; selection-color:{SEL_FG};
}}
QLineEdit:focus, QComboBox:focus,
QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border-color:{BLUE};
}}
QComboBox::drop-down {{ border:none; }}
QComboBox QAbstractItemView {{
    background:white; border:1px solid {BORDER}; border-radius:6px;
    selection-background-color:{BLUE_LT}; selection-color:{SEL_FG};
    outline:none;
}}

/* ── buttons ── */
QPushButton {{
    background:{BLUE}; color:white; border:none;
    border-radius:8px; padding:8px 16px; font-weight:600;
}}
QPushButton:hover   {{ background:{BLUE_DK}; }}
QPushButton:pressed {{ background:#1e40af; }}
QPushButton:disabled{{ background:#cbd5e1; color:#94a3b8; }}
QPushButton#green   {{ background:{GREEN}; }}
QPushButton#green:hover  {{ background:#15803d; }}
QPushButton#red     {{ background:{RED}; }}
QPushButton#red:hover    {{ background:#b91c1c; }}
QPushButton#ghost   {{ background:transparent; color:{BLUE}; border:1.5px solid {BLUE}; }}
QPushButton#ghost:hover  {{ background:{BLUE_LT}; }}
QPushButton#muted   {{ background:{BG}; color:{TEXT}; border:1.5px solid {BORDER}; }}
QPushButton#muted:hover  {{ background:#e2e8f0; }}
QPushButton#amber   {{ background:{AMBER}; color:white; }}
QPushButton#amber:hover  {{ background:#b45309; }}

/* ── table ── */
QTableWidget {{
    background:white; border:none; outline:none;
    gridline-color:#F1F5F9;
    selection-background-color:{SEL_BG};
    selection-color:{SEL_FG};
}}
QTableWidget::item {{
    padding:8px 6px;
    border-bottom:1px solid #F1F5F9;
    color:{TEXT};
}}
QTableWidget::item:selected {{
    background:{SEL_BG};
    color:{SEL_FG};
}}
QTableWidget::item:alternate {{
    background:{ROW_ALT};
}}
QHeaderView::section {{
    background:#F8FAFC; color:{MUTED};
    font-weight:700; font-size:11px;
    padding:10px 6px; border:none;
    border-bottom:2px solid {BORDER};
    letter-spacing:0.5px;
}}
QHeaderView::section:first {{ border-radius:0; }}

/* ── scrollbars ── */
QScrollBar:vertical {{
    background:#F8FAFC; width:6px; border-radius:3px; border:none;
}}
QScrollBar::handle:vertical {{
    background:#c1c9d6; border-radius:3px; min-height:24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0; }}
QScrollBar:horizontal {{
    background:#F8FAFC; height:6px; border-radius:3px; border:none;
}}
QScrollBar::handle:horizontal {{
    background:#c1c9d6; border-radius:3px; min-width:24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width:0; }}

/* ── tabs ── */
QTabWidget::pane       {{ border:none; background:transparent; margin-top:4px; }}
QTabBar::tab {{
    background:transparent; color:{MUTED};
    padding:9px 18px; border:none;
    font-weight:600; font-size:13px;
    border-bottom:2px solid transparent;
}}
QTabBar::tab:selected  {{ color:{BLUE}; border-bottom:2px solid {BLUE}; }}
QTabBar::tab:hover:!selected {{ color:{TEXT}; }}

/* ── labels ── */
QLabel#h1  {{ font-size:22px; font-weight:700; color:{TEXT}; background:transparent; }}
QLabel#h2  {{ font-size:15px; font-weight:700; color:{TEXT}; background:transparent; }}
QLabel#sub {{ font-size:12px; color:{MUTED}; background:transparent; }}
QLabel#kv  {{ font-size:28px; font-weight:800; background:transparent; }}

/* ── sidebar ── */
QListWidget#sidebar {{
    background:{SIDEBAR}; border:none; outline:none;
    font-size:13px; font-weight:500;
}}
QListWidget#sidebar::item {{
    color:#94a3b8; padding:11px 16px;
    margin:2px 8px; border-radius:8px;
}}
QListWidget#sidebar::item:selected {{
    background:{SIDEBAR_SEL}; color:white; font-weight:600;
}}
QListWidget#sidebar::item:hover:!selected {{
    background:{SIDEBAR_HVR}; color:white;
}}

/* ── splitter ── */
QSplitter::handle {{ background:{BORDER}; }}
"""

# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────
def mkcard():
    f = QFrame(); f.setObjectName("card")
    l = QVBoxLayout(f); l.setContentsMargins(20,16,20,16); l.setSpacing(10)
    return f, l

def mkpanel():
    f = QFrame(); f.setObjectName("panel")
    l = QVBoxLayout(f); l.setContentsMargins(14,12,14,12); l.setSpacing(8)
    return f, l

def lbl(text, obj=None, style=None):
    w = QLabel(text)
    if obj:   w.setObjectName(obj)
    if style: w.setStyleSheet(style)
    return w

def mk_btn(text, name=None, h=36, w=None):
    b = QPushButton(text)
    if name: b.setObjectName(name)
    b.setFixedHeight(h)
    if w: b.setFixedWidth(w)
    return b

def mk_field(ph="", fw=None):
    e = QLineEdit(); e.setPlaceholderText(ph)
    e.setFixedHeight(34)
    if fw: e.setFixedWidth(fw)
    return e

def mk_combo():
    c = QComboBox(); c.setFixedHeight(34); return c

def mk_date():
    d = QDateEdit(); d.setCalendarPopup(True)
    d.setDate(QDate.currentDate()); d.setDisplayFormat("yyyy-MM-dd")
    d.setFixedHeight(34); return d

def mk_spin(lo=0, hi=9999, sfx=""):
    s = QSpinBox(); s.setRange(lo, hi)
    if sfx: s.setSuffix(sfx)
    s.setFixedHeight(34); return s

def mk_dspin(lo=0.0, hi=99999.0, dec=2, pfx=""):
    s = QDoubleSpinBox(); s.setRange(lo, hi); s.setDecimals(dec)
    if pfx: s.setPrefix(pfx)
    s.setFixedHeight(34); return s

def ti(val, center=False):
    """Make a non-editable QTableWidgetItem."""
    it = QTableWidgetItem(str(val) if val is not None else "—")
    it.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
    if center:
        it.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
    else:
        it.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    return it

def ti_color(val, color, bold=False, center=True):
    it = ti(val, center)
    it.setForeground(QColor(color))
    if bold: it.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    return it

def setup_table(t, headers, stretch_last=True):
    """Configure a QTableWidget with standard settings."""
    t.setColumnCount(len(headers))
    t.setHorizontalHeaderLabels(headers)
    t.verticalHeader().setVisible(False)
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    t.setAlternatingRowColors(True)
    t.setSortingEnabled(False)          # keep order stable; enable after fill
    t.setShowGrid(False)
    if stretch_last:
        t.horizontalHeader().setStretchLastSection(True)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

def fill_table(t, rows, col_fmt=None, col_color=None):
    """
    Fill QTableWidget t with rows.
    col_fmt:   {col_index: callable(val)->str}
    col_color: {col_index: callable(val)->(color_str, bold)}
    Keeps column widths stable; does NOT re-enable sorting (caller does that).
    """
    t.setSortingEnabled(False)
    t.setRowCount(0)
    t.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            disp = col_fmt[c](val) if (col_fmt and c in col_fmt) else val
            if col_color and c in col_color:
                color, bold = col_color[c](val)
                it = ti_color(disp, color, bold)
            else:
                it = ti(disp)
            t.setItem(r, c, it)

def toast(win, msg, color=GREEN):
    t = QLabel(msg, win)
    t.setStyleSheet(
        f"background:{color};color:white;border-radius:10px;"
        f"padding:10px 22px;font-weight:600;font-size:13px;"
    )
    t.adjustSize()
    t.move(win.width()//2 - t.width()//2, win.height() - 80)
    t.raise_(); t.show()
    QTimer.singleShot(2600, t.deleteLater)

def confirm_dlg(parent, msg):
    r = QMessageBox.question(
        parent, "Confirm", msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    return r == QMessageBox.StandardButton.Yes

def section_hdr(title, sub=""):
    w = QWidget(); w.setStyleSheet("background:transparent;")
    l = QVBoxLayout(w); l.setContentsMargins(0,0,0,0); l.setSpacing(1)
    l.addWidget(lbl(title,"h1")); 
    if sub: l.addWidget(lbl(sub,"sub"))
    return w

def badge_item(text, bg, fg="white"):
    """Return a styled label suitable for use inside a layout."""
    b = QLabel(text)
    b.setStyleSheet(
        f"background:{bg};color:{fg};border-radius:5px;"
        f"padding:2px 8px;font-weight:600;font-size:11px;"
    )
    b.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return b

# ─────────────────────────────────────────────────────────────
#  BASE CRUD PAGE  (stable layout, no resize glitches)
# ─────────────────────────────────────────────────────────────
class CRUDPage(QWidget):
    PAGE_TITLE = "Records"
    PAGE_SUB   = ""
    HEADERS    = []          # table column headers
    FORM_COLS  = 4           # fields per row in form grid

    def __init__(self):
        super().__init__()
        self._pk       = None
        self._all_rows = []
        self._build_base()
        self.refresh()

    # ── scaffold ──────────────────────────────────────────────
    def _build_base(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24,20,24,20)
        root.setSpacing(12)

        # header row
        hrow = QHBoxLayout(); hrow.setSpacing(10)
        hrow.addWidget(section_hdr(self.PAGE_TITLE, self.PAGE_SUB), stretch=1)

        self._count_lbl = lbl("", style=f"color:{MUTED};font-size:12px;")
        hrow.addWidget(self._count_lbl)

        self._search = mk_field(f"🔍  Search {self.PAGE_TITLE}…", fw=240)
        self._search.textChanged.connect(self._filter)
        hrow.addWidget(self._search)

        rb = mk_btn("↺  Refresh","ghost",w=96)
        rb.clicked.connect(self.refresh)
        hrow.addWidget(rb)
        root.addLayout(hrow)

        # Use a splitter so the table and form share space stably on resize
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)

        # ── table wrapper ─────────────────────────────────────
        tbl_wrap = QFrame(); tbl_wrap.setObjectName("card")
        tbl_lay  = QVBoxLayout(tbl_wrap)
        tbl_lay.setContentsMargins(0,0,0,0); tbl_lay.setSpacing(0)

        self.table = QTableWidget()
        setup_table(self.table, self.HEADERS)
        self.table.clicked.connect(self._row_clicked)
        # Give each column an initial equal share; user can resize
        tbl_lay.addWidget(self.table)
        splitter.addWidget(tbl_wrap)

        # ── form card ─────────────────────────────────────────
        form_wrap, form_lay = mkcard()

        fhdr = QHBoxLayout()
        self._form_lbl = lbl("Add New Record","h2")
        fhdr.addWidget(self._form_lbl, stretch=1)
        dot = QFrame(); dot.setFixedSize(8,8)
        dot.setStyleSheet(f"background:{GREEN};border-radius:4px;")
        conn = lbl("Connected", style=f"color:{GREEN};font-weight:600;font-size:11px;background:transparent;")
        fhdr.addWidget(dot); fhdr.addWidget(conn)
        form_lay.addLayout(fhdr)

        # grid for fields – built by subclass
        self._fgrid = QGridLayout()
        self._fgrid.setSpacing(8)
        self._fgrid.setHorizontalSpacing(14)
        fields = self.build_form()           # [(label, widget), ...]
        for idx,(ltext,widget) in enumerate(fields):
            r = (idx // self.FORM_COLS)*2
            c =  idx %  self.FORM_COLS
            cap = QLabel(ltext)
            cap.setStyleSheet(f"font-size:11px;font-weight:600;color:{MUTED};")
            self._fgrid.addWidget(cap,    r,   c)
            self._fgrid.addWidget(widget, r+1, c)
        form_lay.addLayout(self._fgrid)

        # extra form content (subclass can override _extra_form)
        self._extra_form(form_lay)

        # buttons
        brow = QHBoxLayout(); brow.setSpacing(8)
        self.b_add    = mk_btn("＋  Add",    "green", h=36)
        self.b_update = mk_btn("✎  Update",  None,    h=36)
        self.b_delete = mk_btn("🗑  Delete",  "red",   h=36)
        self.b_clear  = mk_btn("✕  Clear",   "muted", h=36)
        self.b_add   .clicked.connect(self._do_add)
        self.b_update.clicked.connect(self._do_update)
        self.b_delete.clicked.connect(self._do_delete)
        self.b_clear .clicked.connect(self._clear_form)
        brow.addWidget(self.b_add)
        brow.addWidget(self.b_update)
        brow.addWidget(self.b_delete)
        brow.addStretch()
        brow.addWidget(self.b_clear)
        form_lay.addLayout(brow)
        splitter.addWidget(form_wrap)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, stretch=1)

    def _extra_form(self, lay): pass   # hook for subclasses

    # ── data ──────────────────────────────────────────────────
    def refresh(self):
        try:
            rows = self.fetch_rows()
            self._all_rows = rows
            self._render(rows)
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))

    def _render(self, rows):
        fill_table(self.table, rows,
                   col_fmt   = self.col_fmt(),
                   col_color = self.col_color())
        self._count_lbl.setText(
            f"{len(rows)} record{'s' if len(rows)!=1 else ''}"
        )
        # resize columns to content but cap at 300 px
        self.table.resizeColumnsToContents()
        for i in range(self.table.columnCount()-1):   # last col stretches
            if self.table.columnWidth(i) > 300:
                self.table.setColumnWidth(i, 300)

    def _filter(self, text):
        t = text.strip().lower()
        filtered = self._all_rows if not t else [
            row for row in self._all_rows
            if any(t in str(v).lower() for v in row if v is not None)
        ]
        self._render(filtered)
        total = len(self._all_rows)
        shown = len(filtered)
        self._count_lbl.setText(
            f"{shown} of {total}" if t else f"{total} record{'s' if total!=1 else ''}"
        )

    def _row_clicked(self, idx):
        r = idx.row()
        row_data = [
            (self.table.item(r,c).text() if self.table.item(r,c) else "")
            for c in range(self.table.columnCount())
        ]
        self._pk = row_data[0]
        self._form_lbl.setText("Edit Record")
        self.populate_form(row_data)

    # ── CRUD ──────────────────────────────────────────────────
    def _do_add(self):
        v = self.read_form()
        if v is None: return
        try:
            begin(); self.sql_insert(v); commit()
            self.refresh(); self._clear_form()
            toast(self.window(), "✔  Record added", GREEN)
        except Exception as e:
            rollback(); QMessageBox.critical(self,"Insert Error",str(e))

    def _do_update(self):
        if not self._pk:
            QMessageBox.warning(self,"No Selection","Select a row first."); return
        v = self.read_form()
        if v is None: return
        try:
            begin(); self.sql_update(self._pk, v); commit()
            self.refresh()
            toast(self.window(), "✔  Record updated", BLUE)
        except Exception as e:
            rollback(); QMessageBox.critical(self,"Update Error",str(e))

    def _do_delete(self):
        if not self._pk:
            QMessageBox.warning(self,"No Selection","Select a row first."); return
        if confirm_dlg(self, "Permanently delete this record?"):
            try:
                begin(); self.sql_delete(self._pk); commit()
                self._pk = None; self.refresh(); self._clear_form()
                toast(self.window(), "🗑  Deleted", RED)
            except Exception as e:
                rollback(); QMessageBox.critical(self,"Delete Error",str(e))

    def _clear_form(self):
        self._pk = None
        self._form_lbl.setText("Add New Record")
        self.table.clearSelection()
        self.clear_form()

    # ── overrideable ──────────────────────────────────────────
    def fetch_rows(self):              return []
    def build_form(self):              return []
    def read_form(self):               return {}
    def populate_form(self, row):      pass
    def clear_form(self):              pass
    def sql_insert(self, v):           pass
    def sql_update(self, pk, v):       pass
    def sql_delete(self, pk):          pass
    def col_fmt(self):                 return {}
    def col_color(self):               return {}

# ─────────────────────────────────────────────────────────────
#  STUDENTS  (rich table: package + latest exam result)
# ─────────────────────────────────────────────────────────────
class StudentsPage(CRUDPage):
    PAGE_TITLE = "Students"
    PAGE_SUB   = "Full student overview — package, exam result, payment balance"
    HEADERS    = ["ID","First Name","Last Name","Phone","Email","Registered",
                  "Package","Exam Result","Total Paid (€)"]
    FORM_COLS  = 4

    def build_form(self):
        self.w_first = mk_field("First name")
        self.w_last  = mk_field("Last name")
        self.w_phone = mk_field("+39 …")
        self.w_email = mk_field("email@example.com")
        self.w_date  = mk_date()
        self.w_pkg   = mk_combo()   # only available packages
        self._reload_packages()
        return [
            ("First Name",         self.w_first),
            ("Last Name",          self.w_last),
            ("Phone",              self.w_phone),
            ("Email",              self.w_email),
            ("Registration Date",  self.w_date),
            ("Assign Package",     self.w_pkg),
        ]

    def _reload_packages(self):
        self.w_pkg.clear()
        self.w_pkg.addItem("— None —", None)
        try:
            rows = qry("""
                SELECT p.PackageID, p.PackageName, p.Price
                FROM Package p
                WHERE p.PackageID NOT IN (
                    SELECT PackageID FROM StudentPackage
                    WHERE PackageID IS NOT NULL
                )
                OR p.PackageID IN (
                    SELECT PackageID FROM StudentPackage
                )
                ORDER BY p.PackageName
            """).fetchall()
            # show ALL packages; student picks one; we allow re-use
            rows2 = qry("SELECT PackageID,PackageName,Price FROM Package ORDER BY PackageName").fetchall()
            for r in rows2:
                self.w_pkg.addItem(f"{r[1]}  (€{float(r[2]):,.0f})", r[0])
        except:
            pass

    def refresh(self):
        self._reload_packages()
        super().refresh()

    def fetch_rows(self):
        return qry("""
            SELECT
                s.StudentID,
                s.FirstName,
                s.LastName,
                COALESCE(s.Phone,'—'),
                COALESCE(s.Email,'—'),
                s.RegistrationDate,
                COALESCE(pkg.PackageName,'None'),
                COALESCE(
                    (SELECT e.Result FROM Exam e
                     WHERE e.StudentID=s.StudentID
                     ORDER BY e.ExamDate DESC LIMIT 1),
                    '—'
                ) AS LastExam,
                COALESCE(
                    (SELECT SUM(p.Amount) FROM Payment p
                     WHERE p.StudentID=s.StudentID),
                    0
                ) AS TotalPaid
            FROM Student s
            LEFT JOIN StudentPackage sp ON sp.StudentID=s.StudentID
            LEFT JOIN Package pkg       ON pkg.PackageID=sp.PackageID
            ORDER BY s.StudentID DESC
        """).fetchall()

    def col_color(self):
        def exam_color(val):
            if str(val) == "Passed":  return GREEN, True
            if str(val) == "Failed":  return RED,   True
            return MUTED, False
        def paid_color(val):
            try:
                return (GREEN, True) if float(val) > 0 else (MUTED, False)
            except: return MUTED, False
        return {
            7: exam_color,
            8: paid_color,
        }

    def col_fmt(self):
        return {8: lambda v: f"€ {float(v):,.2f}"}

    def read_form(self):
        fn = self.w_first.text().strip()
        ln = self.w_last.text().strip()
        if not fn or not ln:
            QMessageBox.warning(self,"Required","First and Last name are required.")
            return None
        return dict(
            fn=fn, ln=ln,
            ph=self.w_phone.text().strip(),
            em=self.w_email.text().strip(),
            dt=self.w_date.date().toString("yyyy-MM-dd"),
            pkg=self.w_pkg.currentData()
        )

    def populate_form(self, row):
        # row indices match HEADERS
        self.w_first.setText(row[1]); self.w_last.setText(row[2])
        self.w_phone.setText(row[3]); self.w_email.setText(row[4])
        if row[5] not in ("","—"):
            self.w_date.setDate(QDate.fromString(str(row[5]),"yyyy-MM-dd"))
        # Find package in combo by name
        for i in range(self.w_pkg.count()):
            if self.w_pkg.itemText(i).startswith(row[6]):
                self.w_pkg.setCurrentIndex(i); break

    def clear_form(self):
        for w in (self.w_first,self.w_last,self.w_phone,self.w_email): w.clear()
        self.w_date.setDate(QDate.currentDate())
        self.w_pkg.setCurrentIndex(0)

    def sql_insert(self, v):
        c = qry("INSERT INTO Student(FirstName,LastName,Phone,Email,RegistrationDate)"
                " VALUES(%s,%s,%s,%s,%s)",
                (v['fn'],v['ln'],v['ph'],v['em'],v['dt']))
        sid = c.lastrowid
        if v['pkg']:
            # check if already has a package
            qry("DELETE FROM StudentPackage WHERE StudentID=%s",(sid,))
            qry("INSERT INTO StudentPackage(StudentID,PackageID) VALUES(%s,%s)",
                (sid, v['pkg']))

    def sql_update(self, pk, v):
        qry("UPDATE Student SET FirstName=%s,LastName=%s,Phone=%s,Email=%s,"
            "RegistrationDate=%s WHERE StudentID=%s",
            (v['fn'],v['ln'],v['ph'],v['em'],v['dt'],pk))
        qry("DELETE FROM StudentPackage WHERE StudentID=%s",(pk,))
        if v['pkg']:
            qry("INSERT INTO StudentPackage(StudentID,PackageID) VALUES(%s,%s)",
                (pk,v['pkg']))

    def sql_delete(self, pk):
        qry("DELETE FROM StudentPackage WHERE StudentID=%s",(pk,))
        qry("DELETE FROM Payment WHERE StudentID=%s",(pk,))
        qry("DELETE FROM Exam WHERE StudentID=%s",(pk,))
        qry("DELETE FROM Lesson WHERE StudentID=%s",(pk,))
        qry("DELETE FROM Student WHERE StudentID=%s",(pk,))

    def _extra_form(self, lay):
        # "View Profile" button
        self.b_profile = mk_btn("👁  View Full Profile","ghost",h=34)
        self.b_profile.clicked.connect(self._open_profile)
        lay.addWidget(self.b_profile, alignment=Qt.AlignmentFlag.AlignRight)

    def _open_profile(self):
        if not self._pk:
            QMessageBox.information(self,"Select Student","Click a student row first.")
            return
        row = qry("SELECT FirstName,LastName FROM Student WHERE StudentID=%s",
                  (self._pk,)).fetchone()
        if row:
            dlg = StudentProfileDialog(self, self._pk, f"{row[0]} {row[1]}")
            dlg.exec()

# ─────────────────────────────────────────────────────────────
#  STUDENT PROFILE DIALOG
# ─────────────────────────────────────────────────────────────
class StudentProfileDialog(QDialog):
    def __init__(self, parent, sid, name):
        super().__init__(parent)
        self.setWindowTitle(f"Profile — {name}")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(APP_QSS)

        root = QVBoxLayout(self)
        root.setContentsMargins(24,20,24,20); root.setSpacing(14)

        # summary bar
        bar, blay = mkcard()
        blay.setContentsMargins(16,12,16,12)
        info_row = QHBoxLayout()

        try:
            s = qry("SELECT FirstName,LastName,Phone,Email,RegistrationDate FROM Student WHERE StudentID=%s",(sid,)).fetchone()
            pkg = qry("""SELECT pkg.PackageName,pkg.Price,pkg.NumberOfLessons
                         FROM StudentPackage sp JOIN Package pkg ON pkg.PackageID=sp.PackageID
                         WHERE sp.StudentID=%s""",(sid,)).fetchone()
            total_paid = qry("SELECT COALESCE(SUM(Amount),0) FROM Payment WHERE StudentID=%s",(sid,)).fetchone()[0]
            lesson_hrs = qry("SELECT COALESCE(SUM(DurationHours),0),COUNT(*) FROM Lesson WHERE StudentID=%s",(sid,)).fetchone()
            last_exam  = qry("SELECT Result,Score FROM Exam WHERE StudentID=%s ORDER BY ExamDate DESC LIMIT 1",(sid,)).fetchone()

            def info_block(label, value, color=TEXT):
                w = QWidget(); w.setStyleSheet("background:transparent;")
                vl = QVBoxLayout(w); vl.setContentsMargins(0,0,0,0); vl.setSpacing(2)
                vl.addWidget(lbl(label,style=f"color:{MUTED};font-size:11px;font-weight:600;background:transparent;"))
                vl.addWidget(lbl(str(value),style=f"color:{color};font-size:14px;font-weight:700;background:transparent;"))
                return w

            info_row.addWidget(info_block("Student", f"{s[0]} {s[1]}"))
            info_row.addWidget(info_block("Phone", s[2] or "—"))
            info_row.addWidget(info_block("Email", s[3] or "—"))
            info_row.addWidget(info_block("Registered", str(s[4])))
            info_row.addWidget(info_block("Package", pkg[0] if pkg else "None"))
            info_row.addWidget(info_block("Lessons", f"{int(lesson_hrs[1])}  ({float(lesson_hrs[0]):.1f} h)"))
            exam_color = GREEN if last_exam and last_exam[0]=="Passed" else RED if last_exam else MUTED
            info_row.addWidget(info_block("Last Exam", f"{last_exam[0]} ({last_exam[1]} pts)" if last_exam else "—", exam_color))
            info_row.addWidget(info_block("Total Paid", f"€ {float(total_paid):,.2f}", GREEN))
        except Exception as e:
            info_row.addWidget(lbl(f"Error loading: {e}"))

        blay.addLayout(info_row)
        root.addWidget(bar)

        # tabs
        tabs = QTabWidget()

        def mini_tbl(headers):
            t = QTableWidget()
            setup_table(t, headers)
            return t

        # Lessons
        lt = QWidget(); ll = QVBoxLayout(lt); ll.setContentsMargins(0,8,0,0)
        lesson_tbl = mini_tbl(["Date","Instructor","Vehicle","Duration (h)"])
        rows = qry("""SELECT l.LessonDate,i.InstructorName,
                             CONCAT(v.Model,' (',v.PlateNumber,')'),l.DurationHours
                      FROM Lesson l
                      JOIN Instructor i ON i.InstructorID=l.InstructorID
                      JOIN Vehicle    v ON v.VehicleID=l.VehicleID
                      WHERE l.StudentID=%s ORDER BY l.LessonDate DESC""",(sid,)).fetchall()
        fill_table(lesson_tbl, rows, col_fmt={3: lambda v: f"{float(v):.1f} h"})
        ll.addWidget(lesson_tbl)
        tabs.addTab(lt,"📋  Lessons")

        # Exams
        et = QWidget(); el = QVBoxLayout(et); el.setContentsMargins(0,8,0,0)
        exam_tbl = mini_tbl(["Date","Score","Result"])
        erows = qry("SELECT ExamDate,Score,Result FROM Exam WHERE StudentID=%s ORDER BY ExamDate DESC",(sid,)).fetchall()
        fill_table(exam_tbl, erows,
                   col_color={2: lambda v: (GREEN,True) if v=="Passed" else (RED,True)})
        el.addWidget(exam_tbl)
        tabs.addTab(et,"📝  Exams")

        # Payments
        pt = QWidget(); pl = QVBoxLayout(pt); pl.setContentsMargins(0,8,0,0)
        pay_tbl = mini_tbl(["Date","Amount (€)","Method"])
        prows = qry("SELECT PaymentDate,Amount,PaymentMethod FROM Payment WHERE StudentID=%s ORDER BY PaymentDate DESC",(sid,)).fetchall()
        fill_table(pay_tbl, prows,
                   col_fmt={1: lambda v: f"€ {float(v):,.2f}"},
                   col_color={1: lambda v: (GREEN,True)})
        pl.addWidget(pay_tbl)
        tabs.addTab(pt,"💶  Payments")

        root.addWidget(tabs)

        close_b = mk_btn("Close","muted",h=36,w=100)
        close_b.clicked.connect(self.accept)
        root.addWidget(close_b, alignment=Qt.AlignmentFlag.AlignRight)

# ─────────────────────────────────────────────────────────────
#  INSTRUCTORS
# ─────────────────────────────────────────────────────────────
class InstructorsPage(CRUDPage):
    PAGE_TITLE = "Instructors"
    PAGE_SUB   = "Manage driving instructors"
    HEADERS    = ["ID","Name","Phone","Hire Date","Experience (yrs)","Lessons Taught"]

    def build_form(self):
        self.w_name  = mk_field("Full name")
        self.w_phone = mk_field("+39 …")
        self.w_hire  = mk_date()
        self.w_exp   = mk_spin(0,50," yrs")
        return [
            ("Full Name",        self.w_name),
            ("Phone",            self.w_phone),
            ("Hire Date",        self.w_hire),
            ("Experience (yrs)", self.w_exp),
        ]

    def fetch_rows(self):
        return qry("""
            SELECT i.InstructorID, i.InstructorName, COALESCE(i.Phone,'—'),
                   i.HireDate, i.ExperienceYears,
                   COUNT(l.LessonID) AS lessons_taught
            FROM Instructor i
            LEFT JOIN Lesson l ON l.InstructorID=i.InstructorID
            GROUP BY i.InstructorID
            ORDER BY i.InstructorID DESC
        """).fetchall()

    def read_form(self):
        n = self.w_name.text().strip()
        if not n: QMessageBox.warning(self,"Required","Name required."); return None
        return dict(name=n,phone=self.w_phone.text().strip(),
                    hire=self.w_hire.date().toString("yyyy-MM-dd"),
                    exp=self.w_exp.value())

    def populate_form(self, r):
        self.w_name.setText(r[1]); self.w_phone.setText(r[2])
        if r[3] not in ("","—"):
            self.w_hire.setDate(QDate.fromString(str(r[3]),"yyyy-MM-dd"))
        try: self.w_exp.setValue(int(r[4]))
        except: pass

    def clear_form(self):
        self.w_name.clear(); self.w_phone.clear()
        self.w_hire.setDate(QDate.currentDate()); self.w_exp.setValue(0)

    def sql_insert(self,v):
        qry("INSERT INTO Instructor(InstructorName,Phone,HireDate,ExperienceYears)"
            " VALUES(%s,%s,%s,%s)",(v['name'],v['phone'],v['hire'],v['exp']))

    def sql_update(self,pk,v):
        qry("UPDATE Instructor SET InstructorName=%s,Phone=%s,HireDate=%s,"
            "ExperienceYears=%s WHERE InstructorID=%s",
            (v['name'],v['phone'],v['hire'],v['exp'],pk))

    def sql_delete(self,pk):
        qry("DELETE FROM Instructor WHERE InstructorID=%s",(pk,))

# ─────────────────────────────────────────────────────────────
#  VEHICLES
# ─────────────────────────────────────────────────────────────
class VehiclesPage(CRUDPage):
    PAGE_TITLE = "Vehicles"
    PAGE_SUB   = "Fleet management"
    HEADERS    = ["ID","Model","Plate Number","Year","Lessons Used"]

    def build_form(self):
        self.w_model = mk_field("e.g. Fiat 500")
        self.w_plate = mk_field("AB123CD")
        self.w_year  = mk_spin(1990, 2035)
        self.w_year.setValue(QDate.currentDate().year())
        return [("Model",self.w_model),("Plate",self.w_plate),("Year",self.w_year)]

    def fetch_rows(self):
        return qry("""
            SELECT v.VehicleID,v.Model,v.PlateNumber,v.Year,
                   COUNT(l.LessonID) AS uses
            FROM Vehicle v
            LEFT JOIN Lesson l ON l.VehicleID=v.VehicleID
            GROUP BY v.VehicleID ORDER BY v.VehicleID DESC
        """).fetchall()

    def read_form(self):
        m=self.w_model.text().strip()
        if not m: QMessageBox.warning(self,"Required","Model required."); return None
        return dict(model=m,plate=self.w_plate.text().strip(),year=self.w_year.value())

    def populate_form(self,r):
        self.w_model.setText(r[1]); self.w_plate.setText(r[2])
        try: self.w_year.setValue(int(r[3]))
        except: pass

    def clear_form(self):
        self.w_model.clear(); self.w_plate.clear()
        self.w_year.setValue(QDate.currentDate().year())

    def sql_insert(self,v):
        qry("INSERT INTO Vehicle(Model,PlateNumber,Year) VALUES(%s,%s,%s)",
            (v['model'],v['plate'],v['year']))

    def sql_update(self,pk,v):
        qry("UPDATE Vehicle SET Model=%s,PlateNumber=%s,Year=%s WHERE VehicleID=%s",
            (v['model'],v['plate'],v['year'],pk))

    def sql_delete(self,pk):
        qry("DELETE FROM Vehicle WHERE VehicleID=%s",(pk,))

# ─────────────────────────────────────────────────────────────
#  LESSONS
# ─────────────────────────────────────────────────────────────
class LessonsPage(CRUDPage):
    PAGE_TITLE = "Lessons"
    PAGE_SUB   = "Schedule and track driving lessons"
    HEADERS    = ["ID","Student","Instructor","Vehicle","Date","Duration (h)"]

    def build_form(self):
        self.w_student    = mk_combo()
        self.w_instructor = mk_combo()
        self.w_vehicle    = mk_combo()
        self.w_date       = mk_date()
        self.w_dur        = mk_dspin(0.5,8.0,1)
        self.w_dur.setSingleStep(0.5); self.w_dur.setValue(1.0)
        self._fill_combos()
        return [
            ("Student",        self.w_student),
            ("Instructor",     self.w_instructor),
            ("Vehicle",        self.w_vehicle),
            ("Date",           self.w_date),
            ("Duration (h)",   self.w_dur),
        ]

    def _fill_combos(self):
        self.w_student.clear()
        for r in qry("SELECT StudentID,FirstName,LastName FROM Student ORDER BY FirstName").fetchall():
            self.w_student.addItem(f"{r[1]} {r[2]}", r[0])
        self.w_instructor.clear()
        for r in qry("SELECT InstructorID,InstructorName FROM Instructor ORDER BY InstructorName").fetchall():
            self.w_instructor.addItem(r[1], r[0])
        self.w_vehicle.clear()
        for r in qry("SELECT VehicleID,Model,PlateNumber FROM Vehicle ORDER BY Model").fetchall():
            self.w_vehicle.addItem(f"{r[1]} ({r[2]})", r[0])

    def refresh(self): self._fill_combos(); super().refresh()

    def fetch_rows(self):
        return qry("""
            SELECT l.LessonID,
                   CONCAT(s.FirstName,' ',s.LastName),
                   i.InstructorName,
                   CONCAT(v.Model,' (',v.PlateNumber,')'),
                   l.LessonDate, l.DurationHours
            FROM Lesson l
            JOIN Student    s ON s.StudentID=l.StudentID
            JOIN Instructor i ON i.InstructorID=l.InstructorID
            JOIN Vehicle    v ON v.VehicleID=l.VehicleID
            ORDER BY l.LessonDate DESC, l.LessonID DESC
        """).fetchall()

    def col_fmt(self): return {5: lambda v: f"{float(v):.1f} h"}

    def read_form(self):
        sid=self.w_student.currentData()
        if not sid: QMessageBox.warning(self,"Required","Select a student."); return None
        return dict(sid=sid,iid=self.w_instructor.currentData(),
                    vid=self.w_vehicle.currentData(),
                    date=self.w_date.date().toString("yyyy-MM-dd"),
                    dur=self.w_dur.value())

    def populate_form(self,row):
        r=qry("SELECT StudentID,InstructorID,VehicleID,LessonDate,DurationHours"
              " FROM Lesson WHERE LessonID=%s",(row[0],)).fetchone()
        if not r: return
        for i in range(self.w_student.count()):
            if self.w_student.itemData(i)==r[0]: self.w_student.setCurrentIndex(i); break
        for i in range(self.w_instructor.count()):
            if self.w_instructor.itemData(i)==r[1]: self.w_instructor.setCurrentIndex(i); break
        for i in range(self.w_vehicle.count()):
            if self.w_vehicle.itemData(i)==r[2]: self.w_vehicle.setCurrentIndex(i); break
        if r[3]: self.w_date.setDate(QDate.fromString(str(r[3]),"yyyy-MM-dd"))
        if r[4]: self.w_dur.setValue(float(r[4]))

    def clear_form(self):
        self.w_student.setCurrentIndex(0); self.w_instructor.setCurrentIndex(0)
        self.w_vehicle.setCurrentIndex(0); self.w_date.setDate(QDate.currentDate())
        self.w_dur.setValue(1.0)

    def sql_insert(self,v):
        qry("INSERT INTO Lesson(StudentID,InstructorID,VehicleID,LessonDate,DurationHours)"
            " VALUES(%s,%s,%s,%s,%s)",(v['sid'],v['iid'],v['vid'],v['date'],v['dur']))

    def sql_update(self,pk,v):
        qry("UPDATE Lesson SET StudentID=%s,InstructorID=%s,VehicleID=%s,"
            "LessonDate=%s,DurationHours=%s WHERE LessonID=%s",
            (v['sid'],v['iid'],v['vid'],v['date'],v['dur'],pk))

    def sql_delete(self,pk):
        qry("DELETE FROM Lesson WHERE LessonID=%s",(pk,))

# ─────────────────────────────────────────────────────────────
#  EXAMS
# ─────────────────────────────────────────────────────────────
class ExamsPage(CRUDPage):
    PAGE_TITLE = "Exams"
    PAGE_SUB   = "Record and track exam results"
    HEADERS    = ["ID","Student","Date","Score","Result"]

    def build_form(self):
        self.w_student = mk_combo()
        self.w_date    = mk_date()
        self.w_score   = mk_spin(0,100," pts")
        self.w_result  = mk_combo()
        self.w_result.addItems(["Passed","Failed"])
        self._fill_students()
        return [
            ("Student",  self.w_student),
            ("Date",     self.w_date),
            ("Score",    self.w_score),
            ("Result",   self.w_result),
        ]

    def _fill_students(self):
        self.w_student.clear()
        for r in qry("SELECT StudentID,FirstName,LastName FROM Student ORDER BY FirstName").fetchall():
            self.w_student.addItem(f"{r[1]} {r[2]}", r[0])

    def refresh(self): self._fill_students(); super().refresh()

    def fetch_rows(self):
        return qry("""
            SELECT e.ExamID,CONCAT(s.FirstName,' ',s.LastName),
                   e.ExamDate,e.Score,e.Result
            FROM Exam e JOIN Student s ON s.StudentID=e.StudentID
            ORDER BY e.ExamDate DESC, e.ExamID DESC
        """).fetchall()

    def col_color(self):
        return {4: lambda v: (GREEN,True) if v=="Passed" else (RED,True)}

    def read_form(self):
        sid=self.w_student.currentData()
        if not sid: QMessageBox.warning(self,"Required","Select a student."); return None
        return dict(sid=sid,date=self.w_date.date().toString("yyyy-MM-dd"),
                    score=self.w_score.value(),result=self.w_result.currentText())

    def populate_form(self,row):
        r=qry("SELECT StudentID,ExamDate,Score,Result FROM Exam WHERE ExamID=%s",(row[0],)).fetchone()
        if not r: return
        for i in range(self.w_student.count()):
            if self.w_student.itemData(i)==r[0]: self.w_student.setCurrentIndex(i); break
        if r[1]: self.w_date.setDate(QDate.fromString(str(r[1]),"yyyy-MM-dd"))
        try: self.w_score.setValue(int(r[2]))
        except: pass
        idx=self.w_result.findText(str(r[3]))
        if idx>=0: self.w_result.setCurrentIndex(idx)

    def clear_form(self):
        self.w_student.setCurrentIndex(0)
        self.w_date.setDate(QDate.currentDate())
        self.w_score.setValue(0); self.w_result.setCurrentIndex(0)

    def sql_insert(self,v):
        qry("INSERT INTO Exam(StudentID,ExamDate,Score,Result) VALUES(%s,%s,%s,%s)",
            (v['sid'],v['date'],v['score'],v['result']))

    def sql_update(self,pk,v):
        qry("UPDATE Exam SET StudentID=%s,ExamDate=%s,Score=%s,Result=%s WHERE ExamID=%s",
            (v['sid'],v['date'],v['score'],v['result'],pk))

    def sql_delete(self,pk):
        qry("DELETE FROM Exam WHERE ExamID=%s",(pk,))

# ─────────────────────────────────────────────────────────────
#  PAYMENTS
# ─────────────────────────────────────────────────────────────
class PaymentsPage(CRUDPage):
    PAGE_TITLE = "Payments"
    PAGE_SUB   = "Track all student payments"
    HEADERS    = ["ID","Student","Amount (€)","Date","Method"]

    def build_form(self):
        self.w_student = mk_combo()
        self.w_amount  = mk_dspin(0,99999,2,"€ ")
        self.w_date    = mk_date()
        self.w_method  = mk_combo()
        self.w_method.addItems(["Cash","Card","Bank Transfer","Online"])
        self._fill_students()
        return [
            ("Student", self.w_student),
            ("Amount",  self.w_amount),
            ("Date",    self.w_date),
            ("Method",  self.w_method),
        ]

    def _fill_students(self):
        self.w_student.clear()
        for r in qry("SELECT StudentID,FirstName,LastName FROM Student ORDER BY FirstName").fetchall():
            self.w_student.addItem(f"{r[1]} {r[2]}", r[0])

    def refresh(self): self._fill_students(); super().refresh()

    def fetch_rows(self):
        return qry("""
            SELECT p.PaymentID,CONCAT(s.FirstName,' ',s.LastName),
                   p.Amount,p.PaymentDate,p.PaymentMethod
            FROM Payment p JOIN Student s ON s.StudentID=p.StudentID
            ORDER BY p.PaymentDate DESC, p.PaymentID DESC
        """).fetchall()

    def col_fmt(self): return {2: lambda v: f"€ {float(v):,.2f}"}
    def col_color(self): return {2: lambda v: (GREEN,True)}

    def read_form(self):
        sid=self.w_student.currentData()
        if not sid: QMessageBox.warning(self,"Required","Select a student."); return None
        return dict(sid=sid,amount=self.w_amount.value(),
                    date=self.w_date.date().toString("yyyy-MM-dd"),
                    method=self.w_method.currentText())

    def populate_form(self,row):
        r=qry("SELECT StudentID,Amount,PaymentDate,PaymentMethod FROM Payment WHERE PaymentID=%s",(row[0],)).fetchone()
        if not r: return
        for i in range(self.w_student.count()):
            if self.w_student.itemData(i)==r[0]: self.w_student.setCurrentIndex(i); break
        try: self.w_amount.setValue(float(r[1]))
        except: pass
        if r[2]: self.w_date.setDate(QDate.fromString(str(r[2]),"yyyy-MM-dd"))
        idx=self.w_method.findText(str(r[3]))
        if idx>=0: self.w_method.setCurrentIndex(idx)

    def clear_form(self):
        self.w_student.setCurrentIndex(0); self.w_amount.setValue(0)
        self.w_date.setDate(QDate.currentDate()); self.w_method.setCurrentIndex(0)

    def sql_insert(self,v):
        qry("INSERT INTO Payment(StudentID,Amount,PaymentDate,PaymentMethod)"
            " VALUES(%s,%s,%s,%s)",(v['sid'],v['amount'],v['date'],v['method']))

    def sql_update(self,pk,v):
        qry("UPDATE Payment SET StudentID=%s,Amount=%s,PaymentDate=%s,"
            "PaymentMethod=%s WHERE PaymentID=%s",
            (v['sid'],v['amount'],v['date'],v['method'],pk))

    def sql_delete(self,pk):
        qry("DELETE FROM Payment WHERE PaymentID=%s",(pk,))

# ─────────────────────────────────────────────────────────────
#  PACKAGES  (manage package catalogue; NOT student assignment)
# ─────────────────────────────────────────────────────────────
class PackagesPage(CRUDPage):
    PAGE_TITLE = "Packages"
    PAGE_SUB   = "Define available training packages — assign them on the Students page"
    HEADERS    = ["ID","Package Name","Description","Price (€)","Lessons","Students Enrolled"]

    def build_form(self):
        self.w_name    = mk_field("e.g. Starter Pack")
        self.w_desc    = mk_field("Short description")
        self.w_price   = mk_dspin(0,9999,2,"€ ")
        self.w_lessons = mk_spin(1,200," lessons")
        return [
            ("Package Name",     self.w_name),
            ("Description",      self.w_desc),
            ("Price",            self.w_price),
            ("Lessons Included", self.w_lessons),
        ]

    def fetch_rows(self):
        try:
            return qry("""
                SELECT p.PackageID, p.PackageName,
                       COALESCE(p.Description,'—'),
                       p.Price, p.NumberOfLessons,
                       COUNT(sp.StudentID) AS enrolled
                FROM Package p
                LEFT JOIN StudentPackage sp ON sp.PackageID=p.PackageID
                GROUP BY p.PackageID
                ORDER BY p.PackageID DESC
            """).fetchall()
        except:
            return []

    def col_fmt(self): return {3: lambda v: f"€ {float(v):,.2f}"}

    def read_form(self):
        n=self.w_name.text().strip()
        if not n: QMessageBox.warning(self,"Required","Name required."); return None
        return dict(name=n,desc=self.w_desc.text().strip(),
                    price=self.w_price.value(),lessons=self.w_lessons.value())

    def populate_form(self,r):
        self.w_name.setText(r[1]); self.w_desc.setText(r[2])
        try: self.w_price.setValue(float(r[3]))
        except: pass
        try: self.w_lessons.setValue(int(r[4]))
        except: pass

    def clear_form(self):
        self.w_name.clear(); self.w_desc.clear()
        self.w_price.setValue(0); self.w_lessons.setValue(1)

    def sql_insert(self,v):
        qry("INSERT INTO Package(PackageName,Description,Price,NumberOfLessons)"
            " VALUES(%s,%s,%s,%s)",(v['name'],v['desc'],v['price'],v['lessons']))

    def sql_update(self,pk,v):
        qry("UPDATE Package SET PackageName=%s,Description=%s,Price=%s,"
            "NumberOfLessons=%s WHERE PackageID=%s",
            (v['name'],v['desc'],v['price'],v['lessons'],pk))

    def sql_delete(self,pk):
        if qry("SELECT COUNT(*) FROM StudentPackage WHERE PackageID=%s",(pk,)).fetchone()[0]>0:
            QMessageBox.warning(None,"In Use","This package is assigned to students. Remove them first.")
            return
        qry("DELETE FROM Package WHERE PackageID=%s",(pk,))

# ─────────────────────────────────────────────────────────────
#  STATISTICS
# ─────────────────────────────────────────────────────────────
class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24,20,24,20); root.setSpacing(14)

        hrow = QHBoxLayout()
        hrow.addWidget(section_hdr("Statistics","Key performance indicators"), stretch=1)
        rb = mk_btn("↺  Refresh","ghost",w=96)
        rb.clicked.connect(self.refresh)
        hrow.addWidget(rb)
        root.addLayout(hrow)

        # KPI row — fixed-height, no dynamic clearing
        self._kpi_frame = QFrame(); self._kpi_frame.setObjectName("card")
        self._kpi_frame.setFixedHeight(130)
        self._kpi_layout = QHBoxLayout(self._kpi_frame)
        self._kpi_layout.setSpacing(0); self._kpi_layout.setContentsMargins(8,8,8,8)
        root.addWidget(self._kpi_frame)

        # two tables side by side, fixed proportions via splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        pay_w,pay_l = mkcard(); pay_l.addWidget(lbl("Recent Payments","h2"))
        self.pay_tbl = QTableWidget()
        setup_table(self.pay_tbl,["Student","Amount","Date","Method"])
        pay_l.addWidget(self.pay_tbl)
        splitter.addWidget(pay_w)

        exam_w,exam_l = mkcard(); exam_l.addWidget(lbl("Recent Exams","h2"))
        self.exam_tbl = QTableWidget()
        setup_table(self.exam_tbl,["Student","Date","Score","Result"])
        exam_l.addWidget(self.exam_tbl)
        splitter.addWidget(exam_w)

        splitter.setStretchFactor(0,1); splitter.setStretchFactor(1,1)
        root.addWidget(splitter, stretch=1)

        # top students
        top_w,top_l = mkcard(); top_l.addWidget(lbl("Top Students by Lesson Hours","h2"))
        self.top_tbl = QTableWidget()
        setup_table(self.top_tbl,["Student","Total Hours","# Lessons","Last Exam","Total Paid"])
        top_l.addWidget(self.top_tbl)
        root.addWidget(top_w)

        self.refresh()

    def _add_kpi(self, icon, title, value, color):
        sep = QFrame()
        sep.setStyleSheet(f"background:transparent;")
        w = QWidget(); w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w); l.setContentsMargins(16,4,16,4); l.setSpacing(2)
        row = QHBoxLayout(); row.setSpacing(6)
        ico = QLabel(icon); ico.setStyleSheet("font-size:18px;background:transparent;")
        tit = QLabel(title); tit.setStyleSheet(f"font-size:11px;font-weight:600;color:{MUTED};background:transparent;")
        row.addWidget(ico); row.addWidget(tit); row.addStretch()
        val = QLabel(str(value)); val.setStyleSheet(f"font-size:26px;font-weight:800;color:{color};background:transparent;")
        l.addLayout(row); l.addWidget(val)
        self._kpi_layout.addWidget(w)
        # vertical divider
        div = QFrame(); div.setFixedWidth(1)
        div.setStyleSheet(f"background:{BORDER};")
        self._kpi_layout.addWidget(div)

    def refresh(self):
        # clear kpi
        while self._kpi_layout.count():
            item = self._kpi_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        try:
            students    = qry("SELECT COUNT(*) FROM Student").fetchone()[0]
            instructors = qry("SELECT COUNT(*) FROM Instructor").fetchone()[0]
            vehicles    = qry("SELECT COUNT(*) FROM Vehicle").fetchone()[0]
            lessons     = qry("SELECT COUNT(*) FROM Lesson").fetchone()[0]
            revenue     = qry("SELECT COALESCE(SUM(Amount),0) FROM Payment").fetchone()[0]
            total_ex    = qry("SELECT COUNT(*) FROM Exam").fetchone()[0]
            passed      = qry("SELECT COUNT(*) FROM Exam WHERE Result='Passed'").fetchone()[0]
            pass_rate   = round(passed*100/total_ex,1) if total_ex else 0
            avg_score   = qry("SELECT COALESCE(AVG(Score),0) FROM Exam").fetchone()[0]

            for icon,title,val,color in [
                ("👤","Students",     students,               BLUE),
                ("🎓","Instructors",  instructors,            GREEN),
                ("🚗","Vehicles",     vehicles,               AMBER),
                ("📋","Lessons",      lessons,                PURPLE),
                ("💶","Revenue",      f"€{float(revenue):,.0f}", GREEN),
                ("✅","Pass Rate",    f"{pass_rate}%",         GREEN if pass_rate>=60 else RED),
                ("⭐","Avg Score",    f"{float(avg_score):.1f}", PURPLE),
            ]:
                self._add_kpi(icon,title,val,color)

            # payments
            rows = qry("""
                SELECT CONCAT(s.FirstName,' ',s.LastName),p.Amount,p.PaymentDate,p.PaymentMethod
                FROM Payment p JOIN Student s ON s.StudentID=p.StudentID
                ORDER BY p.PaymentDate DESC, p.PaymentID DESC LIMIT 10
            """).fetchall()
            fill_table(self.pay_tbl, rows,
                       col_fmt={1:lambda v:f"€ {float(v):,.2f}"},
                       col_color={1:lambda v:(GREEN,True)})

            # exams
            rows = qry("""
                SELECT CONCAT(s.FirstName,' ',s.LastName),e.ExamDate,e.Score,e.Result
                FROM Exam e JOIN Student s ON s.StudentID=e.StudentID
                ORDER BY e.ExamDate DESC, e.ExamID DESC LIMIT 10
            """).fetchall()
            fill_table(self.exam_tbl, rows,
                       col_color={3:lambda v:(GREEN,True) if v=="Passed" else (RED,True)})

            # top students
            rows = qry("""
                SELECT CONCAT(s.FirstName,' ',s.LastName),
                       COALESCE(SUM(l.DurationHours),0),
                       COUNT(l.LessonID),
                       COALESCE((SELECT e.Result FROM Exam e
                                 WHERE e.StudentID=s.StudentID
                                 ORDER BY e.ExamDate DESC LIMIT 1),'—'),
                       COALESCE((SELECT SUM(p.Amount) FROM Payment p
                                 WHERE p.StudentID=s.StudentID),0)
                FROM Student s
                LEFT JOIN Lesson l ON l.StudentID=s.StudentID
                GROUP BY s.StudentID ORDER BY 2 DESC LIMIT 10
            """).fetchall()
            fill_table(self.top_tbl, rows,
                       col_fmt={1:lambda v:f"{float(v):.1f} h",
                                 4:lambda v:f"€ {float(v):,.2f}"},
                       col_color={3:lambda v:(GREEN,True) if v=="Passed" else
                                              (RED,True)   if v=="Failed" else (MUTED,False),
                                  4:lambda v:(GREEN,True)})
        except Exception as e:
            QMessageBox.critical(self,"Stats Error",str(e))

# ─────────────────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    navigate = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24,20,24,20); root.setSpacing(14)

        # header
        hrow = QHBoxLayout()
        hrow.addWidget(section_hdr("Dashboard","Welcome to the Driving School Management System"),stretch=1)
        rb = mk_btn("↺  Refresh","ghost",w=96)
        rb.clicked.connect(self.refresh)
        hrow.addWidget(rb)
        root.addLayout(hrow)

        # KPI row — 6 fixed cards in an HBoxLayout inside a fixed-height frame
        kpi_frame = QFrame(); kpi_frame.setObjectName("card")
        kpi_frame.setFixedHeight(120)
        self._kpi_lay = QHBoxLayout(kpi_frame)
        self._kpi_lay.setSpacing(0); self._kpi_lay.setContentsMargins(8,8,8,8)
        root.addWidget(kpi_frame)

        # middle row: quick actions | upcoming lessons
        mid = QSplitter(Qt.Orientation.Horizontal)
        mid.setChildrenCollapsible(False)

        # quick actions card
        qa_w,qa_l = mkcard(); qa_l.addWidget(lbl("Quick Actions","h2"))
        qa_grid = QGridLayout(); qa_grid.setSpacing(10)
        actions = [
            ("＋  New Student",    1,"green"),
            ("＋  New Lesson",     4,None),
            ("＋  New Payment",    6,"amber"),
            ("＋  Schedule Exam",  5,None),
            ("＋  New Instructor", 2,"muted"),
            ("＋  Add Vehicle",    3,"muted"),
        ]
        for idx,(label,pg,obj) in enumerate(actions):
            b = mk_btn(label,obj,h=40)
            b.clicked.connect(lambda _,p=pg: self.navigate.emit(p))
            qa_grid.addWidget(b, idx//2, idx%2)
        qa_l.addLayout(qa_grid)
        qa_l.addStretch()
        mid.addWidget(qa_w)

        # upcoming lessons
        ul_w,ul_l = mkcard(); ul_l.addWidget(lbl("Upcoming Lessons — next 7 days","h2"))
        self.upcoming_tbl = QTableWidget()
        setup_table(self.upcoming_tbl,["Date","Student","Instructor","Duration"])
        ul_l.addWidget(self.upcoming_tbl)
        mid.addWidget(ul_w)
        mid.setStretchFactor(0,2); mid.setStretchFactor(1,3)
        root.addWidget(mid, stretch=2)

        # bottom row: recent payments | recent exams
        bot = QSplitter(Qt.Orientation.Horizontal)
        bot.setChildrenCollapsible(False)

        rp_w,rp_l = mkcard(); rp_l.addWidget(lbl("Recent Payments","h2"))
        self.pay_tbl = QTableWidget()
        setup_table(self.pay_tbl,["Student","Amount","Date","Method"])
        rp_l.addWidget(self.pay_tbl)
        bot.addWidget(rp_w)

        re_w,re_l = mkcard(); re_l.addWidget(lbl("Recent Exams","h2"))
        self.exam_tbl = QTableWidget()
        setup_table(self.exam_tbl,["Student","Date","Score","Result"])
        re_l.addWidget(self.exam_tbl)
        bot.addWidget(re_w)
        bot.setStretchFactor(0,1); bot.setStretchFactor(1,1)
        root.addWidget(bot, stretch=2)

        self.refresh()

    # ── build a single KPI block ──────────────────────────────
    def _kpi_widget(self, icon, title, value, color):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w); l.setContentsMargins(16,4,16,4); l.setSpacing(2)
        top = QHBoxLayout(); top.setSpacing(6)
        top.addWidget(QLabel(icon, styleSheet="font-size:16px;background:transparent;"))
        top.addWidget(QLabel(title, styleSheet=f"font-size:11px;font-weight:600;color:{MUTED};background:transparent;"))
        top.addStretch()
        l.addLayout(top)
        l.addWidget(QLabel(str(value), styleSheet=f"font-size:24px;font-weight:800;color:{color};background:transparent;"))
        return w

    def refresh(self):
        # clear KPI
        while self._kpi_lay.count():
            item = self._kpi_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        try:
            students    = qry("SELECT COUNT(*) FROM Student").fetchone()[0]
            instructors = qry("SELECT COUNT(*) FROM Instructor").fetchone()[0]
            vehicles    = qry("SELECT COUNT(*) FROM Vehicle").fetchone()[0]
            lessons     = qry("SELECT COUNT(*) FROM Lesson").fetchone()[0]
            revenue     = qry("SELECT COALESCE(SUM(Amount),0) FROM Payment").fetchone()[0]
            rate_row    = qry("SELECT ROUND(SUM(CASE WHEN Result='Passed' THEN 1 ELSE 0 END)*100.0/NULLIF(COUNT(*),0),1) FROM Exam").fetchone()[0]
            pass_rate   = rate_row or 0

            for icon,title,val,color in [
                ("👤","Students",    students,               BLUE),
                ("🎓","Instructors", instructors,            GREEN),
                ("🚗","Vehicles",    vehicles,               AMBER),
                ("📋","Lessons",     lessons,                PURPLE),
                ("💶","Revenue",     f"€{float(revenue):,.0f}", GREEN),
                ("✅","Pass Rate",   f"{pass_rate}%",         GREEN if float(pass_rate)>=60 else RED),
            ]:
                self._kpi_lay.addWidget(self._kpi_widget(icon,title,val,color))
                div = QFrame(); div.setFixedWidth(1)
                div.setStyleSheet(f"background:{BORDER};min-height:40px;")
                self._kpi_lay.addWidget(div)

            # upcoming
            rows = qry("""
                SELECT l.LessonDate,CONCAT(s.FirstName,' ',s.LastName),
                       i.InstructorName,l.DurationHours
                FROM Lesson l
                JOIN Student    s ON s.StudentID=l.StudentID
                JOIN Instructor i ON i.InstructorID=l.InstructorID
                WHERE l.LessonDate BETWEEN CURDATE()
                      AND DATE_ADD(CURDATE(),INTERVAL 7 DAY)
                ORDER BY l.LessonDate LIMIT 8
            """).fetchall()
            fill_table(self.upcoming_tbl, rows,
                       col_fmt={3:lambda v:f"{float(v):.1f} h"})
            if not rows:
                self.upcoming_tbl.setRowCount(1)
                it = ti("No upcoming lessons in the next 7 days")
                it.setForeground(QColor(MUTED))
                self.upcoming_tbl.setItem(0,0,it)

            # recent payments
            rows = qry("""
                SELECT CONCAT(s.FirstName,' ',s.LastName),p.Amount,p.PaymentDate,p.PaymentMethod
                FROM Payment p JOIN Student s ON s.StudentID=p.StudentID
                ORDER BY p.PaymentDate DESC, p.PaymentID DESC LIMIT 7
            """).fetchall()
            fill_table(self.pay_tbl,rows,
                       col_fmt={1:lambda v:f"€ {float(v):,.2f}"},
                       col_color={1:lambda v:(GREEN,True)})

            # recent exams
            rows = qry("""
                SELECT CONCAT(s.FirstName,' ',s.LastName),e.ExamDate,e.Score,e.Result
                FROM Exam e JOIN Student s ON s.StudentID=e.StudentID
                ORDER BY e.ExamDate DESC, e.ExamID DESC LIMIT 7
            """).fetchall()
            fill_table(self.exam_tbl,rows,
                       col_color={3:lambda v:(GREEN,True) if v=="Passed" else (RED,True)})

        except Exception as e:
            QMessageBox.critical(self,"Dashboard Error",str(e))

# ─────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("🏠  Dashboard",    0),
    ("👤  Students",     1),
    ("🎓  Instructors",  2),
    ("🚗  Vehicles",     3),
    ("📋  Lessons",      4),
    ("📝  Exams",        5),
    ("💶  Payments",     6),
    ("📦  Packages",     7),
    ("📊  Statistics",   8),
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚦  Driving School — Management System")
        self.setGeometry(50, 50, 1500, 880)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(APP_QSS)
        self._build()

    def _build(self):
        root_w = QWidget(); self.setCentralWidget(root_w)
        root_l = QHBoxLayout(root_w)
        root_l.setContentsMargins(0,0,0,0); root_l.setSpacing(0)

        # ── SIDEBAR ───────────────────────────────────────────
        sb = QWidget(); sb.setFixedWidth(210)
        sb.setStyleSheet(f"background:{SIDEBAR};")
        sb_l = QVBoxLayout(sb); sb_l.setContentsMargins(0,0,0,0); sb_l.setSpacing(0)

        # logo
        logo = QWidget(); logo.setFixedHeight(68)
        logo.setStyleSheet(f"background:{SIDEBAR};border-bottom:1px solid #334155;")
        ll = QHBoxLayout(logo); ll.setContentsMargins(16,0,12,0); ll.setSpacing(8)
        ll.addWidget(QLabel("🚦", styleSheet="font-size:24px;background:transparent;"))
        ll.addWidget(QLabel("DriveSchool",
                            styleSheet="color:white;font-size:15px;font-weight:700;"
                                       "background:transparent;letter-spacing:0.5px;"))
        ll.addStretch()
        sb_l.addWidget(logo)

        # nav list — NO scroll; all items visible; sized to fit
        self.nav = QListWidget()
        self.nav.setObjectName("sidebar")
        # Disable scroll bars; size sidebar items to always fit
        self.nav.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for label,_ in NAV_ITEMS:
            item = QListWidgetItem(label)
            item.setSizeHint(QSize(210, 46))   # fixed height per item
            self.nav.addItem(item)
        # Make sidebar tall enough for all items
        total_h = 46 * len(NAV_ITEMS) + 20   # items + padding
        self.nav.setMinimumHeight(total_h)
        sb_l.addWidget(self.nav)
        sb_l.addStretch()

        ver = QLabel("v5.0  ·  2025")
        ver.setStyleSheet("color:#475569;font-size:11px;background:transparent;padding:10px 16px;")
        sb_l.addWidget(ver)
        root_l.addWidget(sb)

        # ── PAGE STACK ────────────────────────────────────────
        self.stack = QStackedWidget()
        self.dash  = DashboardPage()
        self.pages = [
            self.dash,
            StudentsPage(),
            InstructorsPage(),
            VehiclesPage(),
            LessonsPage(),
            ExamsPage(),
            PaymentsPage(),
            PackagesPage(),
            StatisticsPage(),
        ]
        for p in self.pages:
            self.stack.addWidget(p)

        root_l.addWidget(self.stack, stretch=1)

        # wire signals
        self.nav.currentRowChanged.connect(self._navigate)
        self.dash.navigate.connect(self._navigate)
        self.nav.setCurrentRow(0)

    def _navigate(self, idx):
        self.nav.blockSignals(True)
        self.nav.setCurrentRow(idx)
        self.nav.blockSignals(False)
        self.stack.setCurrentIndex(idx)
        pg = self.pages[idx]
        if hasattr(pg,"refresh"): pg.refresh()

# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 13))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

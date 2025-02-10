import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QTableWidget, QTableWidgetItem, QTabWidget,
                            QGraphicsScene, QGraphicsView, QGraphicsItem,
                            QGraphicsRectItem, QGraphicsTextItem, QMenu,
                            QComboBox, QHeaderView, QToolTip, QStyledItemDelegate,
                            QStyle, QLineEdit)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (QPen, QBrush, QColor, QPainter, QFont, QCursor,
                        QPainterPath, QPolygonF, QWheelEvent, QPalette)
import math

# Modern Color Scheme
class Colors:
    # Background Colors
    BACKGROUND_DARK = "#1E1E1E"
    BACKGROUND_LIGHT = "#252526"
    CARD_BACKGROUND = "#2D2D30"
    
    # Primary Colors
    PRIMARY = "#3C7AB0"  # Softer blue
    PRIMARY_LIGHT = "#4B8BC2"
    PRIMARY_DARK = "#2C5A8F"
    
    # Accent Colors
    ACCENT_SUCCESS = "#23D18B"
    ACCENT_WARNING = "#D4B45F"  # Softer gold
    ACCENT_DANGER = "#D16B66"   # Softer red
    
    # Text Colors
    TEXT_PRIMARY = "#E8E8E8"    # Slightly softer white
    TEXT_SECONDARY = "#AAAAAA"  # Softer gray
    TEXT_DISABLED = "#6E6E6E"
    
    # Relationship Colors
    PK_COLOR = TEXT_PRIMARY    # White text for primary keys
    FK_COLOR = TEXT_PRIMARY    # White text for foreign keys
    PK_BACKGROUND = "#4D4020"  # Darker gold background
    FK_BACKGROUND = "#1A3043"  # Darker blue background
    
    # Grid Colors
    GRID_LINE = "#3D3D3D"
    ALTERNATE_ROW = "#2A2A2A"

def setup_dark_theme(app):
    """Apply dark theme to the entire application"""
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(Colors.BACKGROUND_DARK))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(Colors.BACKGROUND_LIGHT))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Colors.ALTERNATE_ROW))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Colors.BACKGROUND_DARK))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(Colors.CARD_BACKGROUND))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(Colors.TEXT_PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(Colors.PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(Colors.PRIMARY))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(Colors.TEXT_PRIMARY))

    app.setPalette(dark_palette)
    app.setStyle("Fusion")

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.CARD_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.PRIMARY};
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY};
                color: {Colors.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)

class TableCard(QGraphicsItem):
    def __init__(self, table_name, columns, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.width = 240  # Slightly wider for better readability
        self.header_height = 40
        self.row_height = 28  # Slightly taller rows
        self.height = self.header_height + len(columns) * self.row_height
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        
        # Store connections
        self.connections = []
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget):
        # Draw card shadow
        shadow_rect = self.boundingRect().adjusted(2, 2, 2, 2)
        painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, 10, 10)
        
        # Draw card background
        painter.setBrush(QBrush(QColor(Colors.CARD_BACKGROUND)))
        painter.setPen(QPen(QColor(Colors.PRIMARY), 2))
        painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)
        
        # Draw header
        header_rect = QRectF(0, 0, self.width, self.header_height)
        painter.setBrush(QBrush(QColor(Colors.PRIMARY)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(header_rect, 10, 10)
        
        # Draw table name
        painter.setPen(QPen(QColor(Colors.TEXT_PRIMARY)))
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        painter.setFont(font)
        text_rect = QRectF(10, 0, self.width - 20, self.header_height)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter, self.table_name)
        
        # Draw columns
        painter.setPen(QPen(QColor(Colors.TEXT_SECONDARY)))
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        
        for i, column in enumerate(self.columns):
            y = self.header_height + i * self.row_height
            name_rect = QRectF(10, y, self.width - 20, self.row_height)
            
            # Create column text with type
            col_text = f"{column['name']} ({column['type']})"
            
            # Add relationship indicators with custom styling
            if column['pk']:
                pk_rect = QRectF(8, y + 4, self.width - 16, self.row_height - 8)
                painter.setBrush(QBrush(QColor(Colors.PK_BACKGROUND)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(pk_rect, 4, 4)
                painter.setPen(QPen(QColor(Colors.PK_COLOR)))
                col_text = f"🔑 {col_text}"
            elif column['fk']:
                fk_rect = QRectF(8, y + 4, self.width - 16, self.row_height - 8)
                painter.setBrush(QBrush(QColor(Colors.FK_BACKGROUND)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(fk_rect, 4, 4)
                painter.setPen(QPen(QColor(Colors.FK_COLOR)))
                col_text = f"🔗 {col_text}"
            else:
                painter.setPen(QPen(QColor(Colors.TEXT_SECONDARY)))
            
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignVCenter, col_text)
            
            # Draw separator line
            if i < len(self.columns) - 1:
                painter.setPen(QPen(QColor(Colors.GRID_LINE)))
                painter.drawLine(10, y + self.row_height, self.width - 10, y + self.row_height)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            menu.addAction("View Data", lambda: self.scene().parent().show_table_data(self.table_name))
            menu.exec(QCursor.pos())
        super().mousePressEvent(event)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            for conn in self.connections:
                conn.updatePosition()
        return super().itemChange(change, value)

class Connector(QGraphicsItem):
    def __init__(self, start_card, end_card, start_column, end_column, parent=None):
        super().__init__(parent)
        self.start_card = start_card
        self.end_card = end_card
        self.start_column = start_column
        self.end_column = end_column
        self.start_card.connections.append(self)
        self.end_card.connections.append(self)
        
    def boundingRect(self):
        return self.calculateLine()
        
    def calculateLine(self):
        start_pos = self.start_card.pos()
        end_pos = self.end_card.pos()
        
        # Calculate the points where the line should connect to the cards
        start_x = start_pos.x() + self.start_card.width
        start_y = start_pos.y() + self.start_card.header_height + self.start_column * self.start_card.row_height + self.start_card.row_height/2
        
        end_x = end_pos.x()
        end_y = end_pos.y() + self.end_card.header_height + self.end_column * self.end_card.row_height + self.end_card.row_height/2
        
        # Return bounding rectangle that encompasses the line
        x = min(start_x, end_x)
        y = min(start_y, end_y)
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)
        
        return QRectF(x-5, y-5, width+10, height+10)
        
    def paint(self, painter, option, widget):
        rect = self.calculateLine()
        start_x = self.start_card.pos().x() + self.start_card.width
        start_y = self.start_card.pos().y() + self.start_card.header_height + self.start_column * self.start_card.row_height + self.start_card.row_height/2
        
        end_x = self.end_card.pos().x()
        end_y = self.end_card.pos().y() + self.end_card.header_height + self.end_column * self.end_card.row_height + self.end_card.row_height/2
        
        # Draw connection line
        painter.setPen(QPen(QColor("#2196F3"), 2, Qt.PenStyle.DashLine))
        
        # Calculate control points for curved line
        ctrl1_x = start_x + (end_x - start_x) * 0.4
        ctrl1_y = start_y
        ctrl2_x = start_x + (end_x - start_x) * 0.6
        ctrl2_y = end_y
        
        # Draw curved line
        path = QPainterPath()
        path.moveTo(start_x, start_y)
        path.cubicTo(ctrl1_x, ctrl1_y, ctrl2_x, ctrl2_y, end_x, end_y)
        painter.drawPath(path)
        
        # Draw arrow at end
        arrow_size = 10
        angle = math.atan2(end_y - ctrl2_y, end_x - ctrl2_x)
        arrow_p1 = QPointF(end_x - arrow_size * math.cos(angle - math.pi/6),
                          end_y - arrow_size * math.sin(angle - math.pi/6))
        arrow_p2 = QPointF(end_x - arrow_size * math.cos(angle + math.pi/6),
                          end_y - arrow_size * math.sin(angle + math.pi/6))
        
        painter.setBrush(QBrush(QColor("#2196F3")))
        arrow = QPolygonF([QPointF(end_x, end_y), arrow_p1, arrow_p2])
        painter.drawPolygon(arrow)
        
    def updatePosition(self):
        self.prepareGeometryChange()

class EnhancedGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
    def wheelEvent(self, event: QWheelEvent):
        # Zoom Factor
        zoom_factor = 1.15
        
        # Save the scene pos
        old_pos = self.mapToScene(event.position().toPoint())
        
        # Zoom
        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1.0 / zoom_factor, 1.0 / zoom_factor)
            
        # Get the new position
        new_pos = self.mapToScene(event.position().toPoint())
        
        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

class RelationshipDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.relationships = {}
        
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        
        if index.column() in self.relationships:
            rel = self.relationships[index.column()]
            rect = option.rect
            
            # Draw relationship indicator
            if rel['type'] == 'pk':
                painter.setPen(QPen(QColor("#FFD700")))  # Gold color for PK
                painter.drawRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4)
            elif rel['type'] == 'fk':
                painter.setPen(QPen(QColor("#2196F3")))  # Blue color for FK
                painter.drawRect(rect.x() + 2, rect.y() + 2, rect.width() - 4, rect.height() - 4)

class EnhancedTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.relationship_delegate = RelationshipDelegate()
        self.setItemDelegate(self.relationship_delegate)
        self.relationships = {}
        self.setMouseTracking(True)  # Enable mouse tracking for hover effects
        
        # Style settings
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, pos):
        item = self.itemAt(pos)
        if item:
            col = self.column(item)
            if col in self.relationships:
                menu = QMenu(self)
                rel = self.relationships[col]
                if rel['type'] == 'fk':
                    menu.addAction(f"Go to {rel['ref_table']}", 
                                 lambda: self.parent().parent().show_related_table(rel['ref_table']))
                menu.exec(self.viewport().mapToGlobal(pos))
    
    def mouseMoveEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            col = self.column(item)
            if col in self.relationships:
                rel = self.relationships[col]
                if rel['type'] == 'pk':
                    QToolTip.showText(event.globalPosition().toPoint(), 
                                    f"Primary Key\nUsed as foreign key in: {', '.join(rel['referenced_by'])}")
                elif rel['type'] == 'fk':
                    QToolTip.showText(event.globalPosition().toPoint(), 
                                    f"Foreign Key\nReferences: {rel['ref_table']}.{rel['ref_column']}")
        super().mouseMoveEvent(event)

class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpaceDB Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self.current_db = None
        
        # Set window background
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.BACKGROUND_DARK};
            }}
            QTabWidget::pane {{
                border: 1px solid {Colors.PRIMARY};
                background-color: {Colors.BACKGROUND_LIGHT};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {Colors.CARD_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.PRIMARY};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {Colors.PRIMARY};
            }}
            QTableWidget {{
                background-color: {Colors.BACKGROUND_LIGHT};
                color: {Colors.TEXT_PRIMARY};
                gridline-color: {Colors.GRID_LINE};
                border: none;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {Colors.CARD_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                padding: 5px;
                border: none;
            }}
            QScrollBar {{
                background-color: {Colors.BACKGROUND_LIGHT};
                width: 12px;
                height: 12px;
            }}
            QScrollBar::handle {{
                background-color: {Colors.PRIMARY};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                background: none;
            }}
            QLineEdit {{
                background-color: {Colors.CARD_BACKGROUND};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.PRIMARY};
                border-radius: 4px;
                padding: 5px;
            }}
        """)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar = QHBoxLayout()
        
        # Database controls
        db_controls = QHBoxLayout()
        self.open_btn = ModernButton("Open Database")
        self.open_btn.clicked.connect(self.open_database)
        db_controls.addWidget(self.open_btn)
        
        # Add search box
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tables and content...")
        self.search_box.textChanged.connect(self.filter_content)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        db_controls.addLayout(search_layout)
        
        # Add layout dropdown
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Grid Layout", "Circular Layout", "Spring Layout"])
        self.layout_combo.currentTextChanged.connect(self.rearrange_cards)
        db_controls.addWidget(QLabel("Layout:"))
        db_controls.addWidget(self.layout_combo)
        
        # View controls
        view_controls = QHBoxLayout()
        self.zoom_in_btn = QPushButton("Zoom In")
        self.zoom_out_btn = QPushButton("Zoom Out")
        self.reset_view_btn = QPushButton("Reset View")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_view_btn.clicked.connect(self.reset_view)
        view_controls.addWidget(self.zoom_in_btn)
        view_controls.addWidget(self.zoom_out_btn)
        view_controls.addWidget(self.reset_view_btn)
        
        # Status label
        self.status_label = QLabel("No database opened")
        
        # Add all controls to toolbar
        toolbar.addLayout(db_controls)
        toolbar.addStretch()
        toolbar.addLayout(view_controls)
        toolbar.addStretch()
        toolbar.addWidget(self.status_label)
        
        layout.addLayout(toolbar)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tables_tab = QWidget()
        self.relations_tab = QWidget()
        
        self.tab_widget.addTab(self.tables_tab, "Tables")
        self.tab_widget.addTab(self.relations_tab, "Relationships")
        
        # Setup tables tab
        tables_layout = QVBoxLayout(self.tables_tab)
        self.table_widget = EnhancedTableWidget()
        tables_layout.addWidget(self.table_widget)
        
        # Setup relations tab with enhanced QGraphicsView
        relations_layout = QVBoxLayout(self.relations_tab)
        self.scene = QGraphicsScene()
        self.view = EnhancedGraphicsView(self.scene)
        relations_layout.addWidget(self.view)
        
        layout.addWidget(self.tab_widget)
        
    def zoom_in(self):
        self.view.scale(1.2, 1.2)
        
    def zoom_out(self):
        self.view.scale(1/1.2, 1/1.2)
        
    def reset_view(self):
        self.view.resetTransform()
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        
    def rearrange_cards(self, layout_type):
        if not self.current_db or not hasattr(self, 'cards'):
            return
            
        cards = list(self.cards.values())
        
        if layout_type == "Grid Layout":
            # Arrange in grid
            cols = int(math.sqrt(len(cards))) + 1
            for i, card in enumerate(cards):
                row = i // cols
                col = i % cols
                card.setPos(col * 250 + 50, row * 300 + 50)
                
        elif layout_type == "Circular Layout":
            # Arrange in circle
            center_x = 600
            center_y = 400
            radius = min(300, 100 * len(cards))
            angle_step = 2 * math.pi / len(cards)
            
            for i, card in enumerate(cards):
                angle = i * angle_step
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                card.setPos(x - card.width/2, y - card.height/2)
                
        else:  # Spring Layout
            # Simple force-directed layout
            iterations = 50
            k = 300  # Optimal distance between nodes
            
            # Initialize random positions
            import random
            for card in cards:
                card.setPos(random.uniform(0, 1000), random.uniform(0, 800))
            
            for _ in range(iterations):
                # Calculate repulsive forces
                for i, card1 in enumerate(cards):
                    fx, fy = 0, 0
                    pos1 = card1.pos()
                    
                    # Repulsion from other cards
                    for card2 in cards:
                        if card1 != card2:
                            pos2 = card2.pos()
                            dx = pos1.x() - pos2.x()
                            dy = pos1.y() - pos2.y()
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist < 1: dist = 1
                            
                            # Repulsive force
                            f = k*k / dist
                            fx += (dx/dist) * f
                            fy += (dy/dist) * f
                    
                    # Attraction along edges
                    for conn in card1.connections:
                        other = conn.end_card if conn.start_card == card1 else conn.start_card
                        pos2 = other.pos()
                        dx = pos1.x() - pos2.x()
                        dy = pos1.y() - pos2.y()
                        dist = math.sqrt(dx*dx + dy*dy)
                        if dist < 1: dist = 1
                        
                        # Attractive force
                        f = dist*dist / k
                        fx -= (dx/dist) * f
                        fy -= (dy/dist) * f
                    
                    # Update position
                    card1.setPos(pos1.x() + fx*0.1, pos1.y() + fy*0.1)
        
        # Update view
        self.view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def open_database(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open SQLite Database",
            "",
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if file_name:
            try:
                self.current_db = sqlite3.connect(file_name)
                self.status_label.setText(f"Connected to: {file_name}")
                self.load_tables()
                self.visualize_relationships()
            except sqlite3.Error as e:
                self.status_label.setText(f"Error: {str(e)}")
    
    def load_tables(self):
        if not self.current_db:
            return
            
        cursor = self.current_db.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Create layout for table buttons
        self.table_buttons_layout = QHBoxLayout()
        table_select_layout = QVBoxLayout()  # Changed to vertical layout
        
        # Add search box specifically for tables
        table_search_layout = QHBoxLayout()
        table_search_label = QLabel("Filter Tables:")
        table_search_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        self.table_search_box = QLineEdit()
        self.table_search_box.setPlaceholderText("Type to filter tables...")
        self.table_search_box.textChanged.connect(self.filter_tables)
        table_search_layout.addWidget(table_search_label)
        table_search_layout.addWidget(self.table_search_box)
        table_select_layout.addLayout(table_search_layout)
        
        # Add table buttons
        self.table_buttons_layout.addStretch()
        for table in tables:
            table_btn = ModernButton(table[0])
            table_btn.clicked.connect(lambda checked, t=table[0]: self.show_table_content(t))
            self.table_buttons_layout.addWidget(table_btn)
        self.table_buttons_layout.addStretch()
        
        table_select_layout.addLayout(self.table_buttons_layout)
        self.tables_tab.layout().insertLayout(0, table_select_layout)
    
    def filter_tables(self):
        search_text = self.table_search_box.text().lower()
        for i in range(self.table_buttons_layout.count()):
            widget = self.table_buttons_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                table_name = widget.text().lower()
                widget.setVisible(search_text in table_name)
    
    def show_table_content(self, table_name):
        cursor = self.current_db.cursor()
        
        # Get column info and relationships
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()
        
        # Get tables that reference this table
        referenced_by = {}
        for other_table in self.get_all_tables():
            if other_table != table_name:
                cursor.execute(f"PRAGMA foreign_key_list({other_table})")
                other_fks = cursor.fetchall()
                for fk in other_fks:
                    if fk[2] == table_name:  # if this table is referenced
                        if fk[4] not in referenced_by:  # referenced column
                            referenced_by[fk[4]] = []
                        referenced_by[fk[4]].append(other_table)
        
        # Get table data
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        
        # Set up table widget
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(columns))
        
        # Clear previous relationships
        self.table_widget.relationships.clear()
        
        # Set headers and collect relationship info
        headers = []
        for i, col in enumerate(columns):
            col_name = col[1]
            col_type = col[2]
            is_pk = bool(col[5])
            
            # Check if it's a foreign key
            is_fk = False
            fk_ref = None
            for fk in foreign_keys:
                if fk[3] == col_name:
                    is_fk = True
                    fk_ref = {'table': fk[2], 'column': fk[4]}
                    break
            
            # Create header with relationship indicators
            if is_pk:
                header_text = f"🔑 {col_name}"
                self.table_widget.relationships[i] = {
                    'type': 'pk',
                    'referenced_by': referenced_by.get(col_name, [])
                }
            elif is_fk:
                header_text = f"🔗 {col_name}"
                self.table_widget.relationships[i] = {
                    'type': 'fk',
                    'ref_table': fk_ref['table'],
                    'ref_column': fk_ref['column']
                }
            else:
                header_text = col_name
            
            headers.append(header_text)
        
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Style the headers based on relationships
        header = self.table_widget.horizontalHeader()
        for i in range(len(columns)):
            if i in self.table_widget.relationships:
                rel = self.table_widget.relationships[i]
                if rel['type'] == 'pk':
                    header.model().setHeaderData(i, Qt.Orientation.Horizontal, 
                                               QColor("#FFD700"), Qt.ItemDataRole.BackgroundRole)
                elif rel['type'] == 'fk':
                    header.model().setHeaderData(i, Qt.Orientation.Horizontal, 
                                               QColor("#2196F3"), Qt.ItemDataRole.BackgroundRole)
        
        # Fill data
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make read-only
                
                # Style cells based on relationships
                if j in self.table_widget.relationships:
                    rel = self.table_widget.relationships[j]
                    if rel['type'] == 'pk':
                        item.setBackground(QColor(Colors.PK_BACKGROUND))  # Darker gold for PK
                        item.setForeground(QColor(Colors.TEXT_PRIMARY))  # White text
                    elif rel['type'] == 'fk':
                        item.setBackground(QColor(Colors.FK_BACKGROUND))  # Darker blue for FK
                        item.setForeground(QColor(Colors.TEXT_PRIMARY))  # White text
                
                self.table_widget.setItem(i, j, item)
        
        self.table_widget.resizeColumnsToContents()
        self.table_widget.resizeRowsToContents()
        
        # Switch to Tables tab
        self.tab_widget.setCurrentWidget(self.tables_tab)
    
    def show_related_table(self, table_name):
        """Show the related table when clicking on a foreign key relationship"""
        self.show_table_content(table_name)
    
    def get_all_tables(self):
        """Get list of all tables in the database"""
        cursor = self.current_db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in cursor.fetchall()]
    
    def get_table_columns(self, table_name):
        """Get column information including relationships for a table"""
        cursor = self.current_db.cursor()
        
        # Get column info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        
        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        foreign_keys = cursor.fetchall()
        
        columns = []
        for col in columns_info:
            column = {
                'name': col[1],
                'type': col[2],
                'pk': bool(col[5]),  # Is primary key
                'fk': False,
                'fk_ref': None
            }
            
            # Check if column is a foreign key
            for fk in foreign_keys:
                if fk[3] == column['name']:
                    column['fk'] = True
                    column['fk_ref'] = {'table': fk[2], 'column': fk[4]}
            
            columns.append(column)
            
        return columns
    
    def visualize_relationships(self):
        if not self.current_db:
            return
            
        self.scene.clear()
        cursor = self.current_db.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Create cards
        self.cards = {}
        for i, table in enumerate(tables):
            table_name = table[0]
            columns = self.get_table_columns(table_name)
            
            # Create card
            card = TableCard(table_name, columns)
            self.scene.addItem(card)
            self.cards[table_name] = card
        
        # Create connections
        for table_name, card in self.cards.items():
            for column in card.columns:
                if column['fk']:
                    ref = column['fk_ref']
                    if ref['table'] in self.cards:
                        ref_card = self.cards[ref['table']]
                        ref_col_idx = next(i for i, col in enumerate(ref_card.columns) 
                                         if col['name'] == ref['column'])
                        
                        connector = Connector(
                            card,
                            ref_card,
                            next(i for i, col in enumerate(card.columns) if col['name'] == column['name']),
                            ref_col_idx
                        )
                        self.scene.addItem(connector)
        
        # Apply initial layout
        self.rearrange_cards(self.layout_combo.currentText())

    def filter_content(self):
        search_text = self.search_box.text().lower()
        
        # Filter table buttons
        for i in range(self.table_buttons_layout.count()):
            widget = self.table_buttons_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton):
                table_name = widget.text().lower()
                widget.setVisible(search_text in table_name)
        
        # Filter table content if a table is currently displayed
        if self.table_widget.rowCount() > 0:
            for row in range(self.table_widget.rowCount()):
                row_visible = False
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if item and search_text in item.text().lower():
                        row_visible = True
                        break
                self.table_widget.setRowHidden(row, not row_visible)

def main():
    app = QApplication(sys.argv)
    setup_dark_theme(app)
    viewer = DatabaseViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
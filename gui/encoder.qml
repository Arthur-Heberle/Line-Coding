import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    title: "8B6T Signal Encoder"
    width: 900
    height: 720
    minimumWidth: 700
    minimumHeight: 500
    visible: true

    // ── Palette — edit here to restyle the whole app ──────────────────────────
    readonly property color bg:       "#080D1C"
    readonly property color surface:  "#0F1629"
    readonly property color border:   "#1E2D4A"
    readonly property color accent:   "#4F46E5"
    readonly property color accentHover: "#4338CA"
    readonly property color txt:      "#E2E8F0"
    readonly property color muted:    "#64748B"
    readonly property color errColor: "#EF4444"
    readonly property color waveBg:   "#050910"

    // ── Typography ────────────────────────────────────────────────────────────
    readonly property string fontUI:   "Ubuntu, Segoe UI, sans-serif"
    readonly property string fontMono: "JetBrains Mono, Courier New, Monospace"

    background: Rectangle { color: root.bg }

    // ── Python → QML signal handlers ──────────────────────────────────────────
    Connections {
        target: encoder

        function onDataChanged() {
            encryptedArea.text = encoder.encrypted

            var bin = encoder.binary
            var parts = []
            for (var i = 0; i < bin.length; i += 8)
                parts.push(bin.substring(i, i + 8))
            binaryArea.text = parts.join(" ")

            waveLabel.text   = "FORMA DE ONDA — TRITS  (" + encoder.trits.length + ")"
            waveCanvas.trits = encoder.trits

            resultsPanel.visible = true
            errorLabel.visible   = false
        }

        function onErrorOccurred(msg) {
            errorLabel.text    = msg
            errorLabel.visible = true
        }
    }

    Connections {
        target: serialBridge

        function onErrorOccurred(msg) {
            errorLabel.text    = msg
            errorLabel.visible = true
        }
    }

    // ── Scrollable main content ───────────────────────────────────────────────
    Flickable {
        id: mainFlick
        anchors.fill: parent
        contentWidth:  width
        contentHeight: mainContent.height
        clip: true

        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        Column {
            id: mainContent
            width: mainFlick.width
            spacing: 0

            // Top padding
            Item { width: 1; height: 40 }

            // ── Header ────────────────────────────────────────────────────────
            Item {
                width: parent.width
                height: headerRow.implicitHeight

                RowLayout {
                    id: headerRow
                    anchors { left: parent.left; right: parent.right
                              leftMargin: 40; rightMargin: 40 }
                    spacing: 0

                    Text {
                        text: "8<font color='%1'>B</font>6<font color='%1'>T</font>".arg(root.accent)
                        textFormat: Text.RichText
                        color: root.txt
                        font.family: root.fontMono
                        font.pixelSize: 30
                        font.bold: true
                        font.letterSpacing: -1
                    }

                    Item { width: 20 }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 1
                        color: root.border
                    }

                    Item { width: 20 }

                    Text {
                        text: "Signal Encoder"
                        color: root.muted
                        font.pixelSize: 10
                        font.letterSpacing: 3
                    }
                }
            }

            Item { width: 1; height: 36 }

            // ── Form ──────────────────────────────────────────────────────────
            Item {
                width: parent.width
                height: formRow.implicitHeight

                RowLayout {
                    id: formRow
                    anchors { left: parent.left; right: parent.right
                              leftMargin: 40; rightMargin: 40 }
                    spacing: 12

                    // Message field
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: "MENSAGEM"
                            color: root.muted
                            font.pixelSize: 10
                            font.letterSpacing: 2
            font.bold: true
                        }

                        TextField {
                            id: msgInput
                            Layout.fillWidth: true
                            placeholderText: "Digite a mensagem a codificar…"
                            color: root.txt
                            placeholderTextColor: root.muted
                            font.family: root.fontMono
                            font.pixelSize: 14
                            leftPadding: 14; rightPadding: 14
                            topPadding: 12;  bottomPadding: 12

                            background: Rectangle {
                                color: root.surface
                                radius: 8
                                border.color: parent.activeFocus ? root.accent : root.border
                                border.width: 1
                            }

                            Keys.onReturnPressed: encoder.encode(msgInput.text, keyInput.text)
                        }
                    }

                    // Key field
                    ColumnLayout {
                        spacing: 8

                        Text {
                            text: "CHAVE VIGENÈRE"
                            color: root.muted
                            font.pixelSize: 10
                            font.letterSpacing: 2
                            font.bold: true
                        }

                        TextField {
                            id: keyInput
                            implicitWidth: 210
                            placeholderText: "Chave secreta"
                            color: root.txt
                            placeholderTextColor: root.muted
                            font.family: root.fontMono
                            font.pixelSize: 14
                            leftPadding: 14; rightPadding: 14
                            topPadding: 12;  bottomPadding: 12

                            background: Rectangle {
                                color: root.surface
                                radius: 8
                                border.color: parent.activeFocus ? root.accent : root.border
                                border.width: 1
                            }

                            Keys.onReturnPressed: encoder.encode(msgInput.text, keyInput.text)
                        }
                    }
                }
            }

            Item { width: 1; height: 14 }

            // ── Button + error ─────────────────────────────────────────────────
            Item {
                width: parent.width
                height: actionsRow.implicitHeight

                RowLayout {
                    id: actionsRow
                    anchors { left: parent.left; right: parent.right
                              leftMargin: 40; rightMargin: 40 }
                    spacing: 16

                    Button {
                        id: encodeBtn
                        text: "Codificar"
                        implicitHeight: 44
                        leftPadding: 36; rightPadding: 36

                        background: Rectangle {
                            color: parent.down ? root.accentHover
                                 : parent.hovered ? root.accentHover
                                 : root.accent
                            radius: 8
                        }

                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            font.pixelSize: 14
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        onClicked: encoder.encode(msgInput.text, keyInput.text)
                    }

                    Text {
                        id: errorLabel
                        visible: false
                        color: root.errColor
                        font.pixelSize: 13
                    }

                    Item { Layout.fillWidth: true }
                }
            }

            Item { width: 1; height: 24 }

            // ── Serial controls ───────────────────────────────────────────────
            Item {
                width: parent.width
                height: serialRow.implicitHeight

                RowLayout {
                    id: serialRow
                    anchors { left: parent.left; right: parent.right
                              leftMargin: 40; rightMargin: 40 }
                    spacing: 12

                    ColumnLayout {
                        Layout.preferredWidth: 220
                        spacing: 8

                        Text {
                            text: "PORTA SERIAL"
                            color: root.muted
                            font.pixelSize: 10
                            font.letterSpacing: 2
                            font.bold: true
                        }

                        TextField {
                            id: portInput
                            Layout.fillWidth: true
                            text: "/dev/ttyACM0"
                            color: root.txt
                            placeholderTextColor: root.muted
                            font.family: root.fontMono
                            font.pixelSize: 14
                            leftPadding: 14; rightPadding: 14
                            topPadding: 12;  bottomPadding: 12

                            background: Rectangle {
                                color: root.surface
                                radius: 8
                                border.color: parent.activeFocus ? root.accent : root.border
                                border.width: 1
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.preferredWidth: 120
                        spacing: 8

                        Text {
                            text: "BAUD"
                            color: root.muted
                            font.pixelSize: 10
                            font.letterSpacing: 2
                            font.bold: true
                        }

                        TextField {
                            id: baudInput
                            Layout.fillWidth: true
                            text: "115200"
                            color: root.txt
                            placeholderTextColor: root.muted
                            font.family: root.fontMono
                            font.pixelSize: 14
                            leftPadding: 14; rightPadding: 14
                            topPadding: 12;  bottomPadding: 12

                            background: Rectangle {
                                color: root.surface
                                radius: 8
                                border.color: parent.activeFocus ? root.accent : root.border
                                border.width: 1
                            }
                        }
                    }

                    Button {
                        id: connectBtn
                        text: serialBridge !== null && serialBridge.connected ? "Desconectar" : "Conectar"
                        implicitHeight: 44
                        Layout.alignment: Qt.AlignBottom
                        leftPadding: 24; rightPadding: 24

                        background: Rectangle {
                            color: parent.down || parent.hovered ? root.accentHover : root.accent
                            radius: 8
                        }

                        contentItem: Text {
                            text: parent.text
                            color: "white"
                            font.pixelSize: 14
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        onClicked: {
                            if (serialBridge.connected)
                                serialBridge.disconnectSerial()
                            else
                                serialBridge.connectSerial(portInput.text, baudInput.text)
                        }
                    }

                    Button {
                        id: sendBtn
                        text: "Enviar TRITS"
                        implicitHeight: 44
                        Layout.alignment: Qt.AlignBottom
                        enabled: serialBridge !== null && serialBridge.connected && encoder.payload.length > 0
                        leftPadding: 24; rightPadding: 24

                        background: Rectangle {
                            color: !parent.enabled ? root.border
                                 : parent.down || parent.hovered ? root.accentHover
                                 : root.accent
                            radius: 8
                        }

                        contentItem: Text {
                            text: parent.text
                            color: parent.enabled ? "white" : root.muted
                            font.pixelSize: 14
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        onClicked: serialBridge.sendPayload(encoder.payload)
                    }

                    Text {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignBottom
                        text: serialBridge !== null ? serialBridge.status : "Desconectado."
                        color: root.muted
                        font.pixelSize: 12
                        wrapMode: Text.WrapAnywhere
                    }
                }
            }

            Item { width: 1; height: 24 }

            // ── Results panel ─────────────────────────────────────────────────
            Rectangle {
                id: resultsPanel
                x: 40
                width: parent.width - 80
                visible: false
                color: root.surface
                radius: 12
                border.color: root.border
                border.width: 1
                height: resultsCol.implicitHeight

                Column {
                    id: resultsCol
                    width: parent.width
                    spacing: 0

                    // ── Texto Cifrado ─────────────────────────────────────────
                    Column {
                        width: parent.width
                        spacing: 10
                        topPadding: 18; bottomPadding: 18
                        leftPadding: 22; rightPadding: 22

                        Text {
                            text: "TEXTO CIFRADO"
                            color: root.accent
                            font.pixelSize: 10
                            font.letterSpacing: 2.5
                            font.bold: true
                        }

                        ScrollView {
                            width: parent.width - parent.leftPadding - parent.rightPadding
                            height: 54
                            clip: true

                            TextArea {
                                id: encryptedArea
                                readOnly: true
                                wrapMode: Text.WrapAnywhere
                                color: root.txt
                                font.family: root.fontMono
                                font.pixelSize: 13
                                leftPadding: 14; rightPadding: 14
                                topPadding: 10;  bottomPadding: 10
                                selectByMouse: true
                                background: Rectangle { color: root.bg; radius: 6 }
                            }
                        }
                    }

                    // Divider
                    Rectangle { width: parent.width; height: 1; color: root.border }

                    // ── Binário ───────────────────────────────────────────────
                    Column {
                        width: parent.width
                        spacing: 10
                        topPadding: 18; bottomPadding: 18
                        leftPadding: 22; rightPadding: 22

                        Text {
                            text: "BINÁRIO"
                            color: root.accent
                            font.pixelSize: 10
                            font.letterSpacing: 2.5
                            font.bold: true
                        }

                        ScrollView {
                            width: parent.width - parent.leftPadding - parent.rightPadding
                            height: 80
                            clip: true

                            TextArea {
                                id: binaryArea
                                readOnly: true
                                wrapMode: Text.WrapAnywhere
                                color: root.txt
                                font.family: root.fontMono
                                font.pixelSize: 13
                                leftPadding: 14; rightPadding: 14
                                topPadding: 10;  bottomPadding: 10
                                selectByMouse: true
                                background: Rectangle { color: root.bg; radius: 6 }
                            }
                        }
                    }

                    // Divider
                    Rectangle { width: parent.width; height: 1; color: root.border }

                    // ── Forma de Onda ─────────────────────────────────────────
                    Column {
                        width: parent.width
                        spacing: 10
                        topPadding: 18; bottomPadding: 18
                        leftPadding: 22; rightPadding: 22

                        Text {
                            id: waveLabel
                            text: "FORMA DE ONDA — TRITS"
                            color: root.accent
                            font.pixelSize: 10
                            font.letterSpacing: 2.5
                            font.bold: true
                        }

                        // Waveform container
                        Rectangle {
                            id: waveContainer
                            width: parent.width - parent.leftPadding - parent.rightPadding
                            height: 168
                            color: root.waveBg
                            radius: 6
                            clip: true

                            // Horizontal scroll for wide waveforms
                            Flickable {
                                id: waveFlick
                                anchors.fill: parent
                                contentWidth: waveCanvas.width
                                contentHeight: height
                                clip: false

                                ScrollBar.horizontal: ScrollBar {
                                    policy: ScrollBar.AsNeeded
                                }

                                // ── Canvas waveform ───────────────────────────
                                Canvas {
                                    id: waveCanvas
                                    property var trits: []
                                    property int drawn: 0

                                    width:  Math.max(waveFlick.width, trits.length * 28 + 70)
                                    height: 160

                                    onTritsChanged: {
                                        drawn = 0
                                        animTimer.restart()
                                    }

                                    // Draws one batch of the step signal
                                    function drawBatch(ctx, from, to, lw, color) {
                                        var ML = 50, TW = 28
                                        var Y1 = 28, Y0 = height / 2, YN = height - 28

                                        ctx.beginPath()
                                        ctx.lineWidth   = lw
                                        ctx.strokeStyle = color
                                        ctx.lineJoin    = "miter"

                                        for (var i = from; i < to; i++) {
                                            var t  = trits[i]
                                            var y  = t === 1 ? Y1 : t === 0 ? Y0 : YN
                                            var x  = ML + i * TW
                                            var xe = x + TW

                                            if (i === 0) {
                                                ctx.moveTo(x, y)
                                            } else {
                                                var tp = trits[i - 1]
                                                var py = tp === 1 ? Y1 : tp === 0 ? Y0 : YN
                                                if (i === from) ctx.moveTo(x, py)
                                                if (py !== y)   ctx.lineTo(x, y)
                                            }
                                            ctx.lineTo(xe, y)
                                        }
                                        ctx.stroke()
                                    }

                                    onPaint: {
                                        if (trits.length === 0) return

                                        var ctx = getContext("2d")
                                        var ML = 50
                                        var Y1 = 28, Y0 = height / 2, YN = height - 28

                                        // First frame: draw background, grid and labels
                                        if (drawn === 0) {
                                            ctx.fillStyle = root.waveBg.toString()
                                            ctx.fillRect(0, 0, width, height)

                                            // Dashed grid lines
                                            ctx.save()
                                            ctx.setLineDash([3, 6])
                                            ctx.lineWidth = 1
                                            var grid = [[Y1, "#1A2845"], [Y0, "#1E3560"], [YN, "#1A2845"]]
                                            for (var g = 0; g < grid.length; g++) {
                                                ctx.strokeStyle = grid[g][1]
                                                ctx.beginPath()
                                                ctx.moveTo(ML, grid[g][0])
                                                ctx.lineTo(width - 20, grid[g][0])
                                                ctx.stroke()
                                            }
                                            ctx.restore()

                                            // Y-axis separator
                                            ctx.strokeStyle = "#1A2845"
                                            ctx.lineWidth = 1
                                            ctx.beginPath()
                                            ctx.moveTo(ML - 6, 8)
                                            ctx.lineTo(ML - 6, height - 8)
                                            ctx.stroke()

                                            // Y labels
                                            ctx.font           = "10px Monospace"
                                            ctx.fillStyle      = "#4A5C7A"
                                            ctx.textAlign      = "right"
                                            ctx.textBaseline   = "middle"
                                            ctx.fillText("+1", ML - 12, Y1)
                                            ctx.fillText(" 0", ML - 12, Y0)
                                            ctx.fillText("−1", ML - 12, YN)
                                        }

                                        if (drawn >= trits.length) return

                                        var end = Math.min(drawn + 6, trits.length)

                                        // Outer glow layer
                                        drawBatch(ctx, drawn, end, 10, "rgba(245,158,11,0.12)")

                                        // Core line with shadow glow
                                        ctx.shadowColor = "#F59E0B"
                                        ctx.shadowBlur  = 8
                                        drawBatch(ctx, drawn, end, 2, "#F59E0B")
                                        ctx.shadowBlur  = 0

                                        drawn = end
                                    }

                                    Timer {
                                        id: animTimer
                                        interval: 16
                                        repeat:   true
                                        onTriggered: {
                                            if (waveCanvas.drawn < waveCanvas.trits.length)
                                                waveCanvas.requestPaint()
                                            else
                                                stop()
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Item { width: 1; height: 40 }
        }
    }
}

import SwiftUI
import UIKit
import CoreText

/// Missouri palette (provisional, 2026-11-06; Nick decides, playbook/05-naming.md), light only. Loyalties split (Cardinals and Blues
/// against Royals and Chiefs; Mizzou against the rest), so the colors come from the state flag (state-prompts/MISSOURI_PROMPT.md; the
/// U.S. flag's web values, since Missouri sets no hex): navy #0A3161 (12.9:1 on white) for titles, tint and accents; red #B31942 (white
/// on it 6.7:1) for the hand-checked guide cards; river blue #8DB8DE only as a pin and card fill under navy text (6.3:1); a deeper red
/// #8A1232 for honors chips; limestone cream #F5F1E8 pages. The names `green`/`gold` are kept from Wisconsin Eats so the shared views
/// read the same; here `green` is flag navy and `gold` is flag red.
enum Theme {
    static let green = Color(hex: 0x0A3161)      // flag navy: titles, tint, primary text accents
    static let green2 = Color(hex: 0x24497E)
    static let gold = Color(hex: 0xB31942)       // flag red: card fills under white text, chips
    static let goldSoft = Color(hex: 0xF6DCE3)   // soft red
    static let lime = Color(hex: 0x8DB8DE)       // river blue, fills only (hand-checked pins, the title shadow), under navy text
    static let limeSoft = Color(hex: 0xDCEAF6)
    static let sand = Color(hex: 0xF5F1E8)       // the Home background, limestone cream
    static let red = Color(hex: 0x8A1232)        // honors chips, deep red
    static let sandstone = Color(hex: 0x8A1232)
    static let teal = Color(hex: 0x2E6E86)       // river accent (5.6:1 on white)
    static let ink = Color(hex: 0x1A1A1A)
    static let ink2 = Color(hex: 0x2E3440)
    static let muted = Color(hex: 0x5B6270)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xEDE7DA)
    static let surface3 = Color(hex: 0xE1DACB)
    static let rule = Color(hex: 0xE1DACB)
    static let rule2 = Color(hex: 0xC8BFAC)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// Missouri Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: the Missouri River, a navy ribbon winding across green bottomland from the west, on a red baseline.
struct Stripes: View {
    var height: CGFloat = 6

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, base = h * 0.80
            ctx.fill(Path(CGRect(x: 0, y: 0, width: w, height: base)), with: .color(Color(hex: 0xDDE8D2)))
            var river = Path()
            let mid = base * 0.5, amp = base * 0.28
            river.move(to: CGPoint(x: 0, y: mid))
            for k in 0...60 {
                let x = CGFloat(k) / 60
                river.addLine(to: CGPoint(x: x * w, y: mid + amp * sin(x * .pi * 3.2)))
            }
            ctx.stroke(river, with: .color(Theme.green), style: StrokeStyle(lineWidth: max(2, base * 0.28), lineCap: .round))
            // the red baseline last
            ctx.fill(Path(CGRect(x: 0, y: base, width: w, height: h - base)), with: .color(Theme.gold))
        }
        .frame(height: height * 2.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}

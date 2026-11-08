// Missouri Eats brand (final: Nick's decision 2026-11-07): the app icon is concept A of
// scripts/icon-concepts.swift, two toasted ravioli and a cup of marinara, on the flag's navy; the shared Eats Ranked icon style,
// state-prompts/ICON-STYLE.md, no backing shape. No Arch, no team or university marks.
// Usage, from mo-eats/: swift scripts/make-brand.swift   -> MissouriEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let NAVY: UInt32 = 0x0A3161, RAV1: UInt32 = 0xC98A3A, RAV2: UInt32 = 0xE0A44E, CUP: UInt32 = 0xF4F1EA, SAUCE: UInt32 = 0xC2361F
let RED: UInt32 = 0xB31942, FIELD: UInt32 = 0xDDE8D2

/// A: two toasted ravioli and a cup of marinara. CoreGraphics y-up, s = canvas size. Identical to icon-concepts.swift's concept A.
func ravioli(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
        CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
    }
    c.setFillColor(rgb(RAV1)); c.addPath(R(0.135, 0.35, 0.34, 0.34, 0.06)); c.fillPath()
    c.setFillColor(rgb(RAV2)); c.addPath(R(0.405, 0.35, 0.34, 0.34, 0.06)); c.fillPath()
    c.setFillColor(rgb(CUP)); c.fillEllipse(in: CGRect(x: 0.645 * s, y: 0.29 * s, width: 0.22 * s, height: 0.22 * s))
    c.setFillColor(rgb(SAUCE)); c.fillEllipse(in: CGRect(x: 0.67 * s, y: 0.315 * s, width: 0.17 * s, height: 0.17 * s))
}

func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(NAVY)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    ravioli(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "MissouriEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): flag navy, the ravioli at the left, the name and tagline at the right, and the app's header band along
/// the bottom: the Missouri River winding across green bottomland on a red baseline (Theme.swift's Stripes).
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(NAVY)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    let band: CGFloat = 64, base: CGFloat = 14, w = CGFloat(W)
    ctx.setFillColor(rgb(FIELD)); ctx.fill(CGRect(x: 0, y: base, width: w, height: band - base))
    let river = CGMutablePath(); let mid = base + (band - base) / 2, amp = (band - base) * 0.28
    river.move(to: CGPoint(x: 0, y: mid))
    for k in 0...120 { let x = CGFloat(k) / 120; river.addLine(to: CGPoint(x: x * w, y: mid + amp * sin(x * .pi * 3.2))) }
    ctx.setStrokeColor(rgb(NAVY)); ctx.setLineWidth(12); ctx.setLineCap(.round); ctx.addPath(river); ctx.strokePath()
    ctx.setFillColor(rgb(RED)); ctx.fill(CGRect(x: 0, y: 0, width: w, height: base))
    ctx.saveGState(); ctx.translateBy(x: 20, y: 80); ravioli(ctx, 540); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 92) ?? NSFont.boldSystemFont(ofSize: 80)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 32) ?? NSFont.boldSystemFont(ofSize: 28)
    NSAttributedString(string: "MISSOURI", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 600, y: 370))
    NSAttributedString(string: "EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 600, y: 276))
    NSAttributedString(string: "BARBECUE, TOASTED RAVS & CUSTARD", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 0.553, green: 0.722, blue: 0.871, alpha: 1)]).draw(at: NSPoint(x: 604, y: 226))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")

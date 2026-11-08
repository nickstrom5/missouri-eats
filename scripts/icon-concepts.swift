// Missouri Eats icon concepts (2026-11-06), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level,
// centred food on the flag's navy #0A3161 (state-prompts/MISSOURI_PROMPT.md), no backing shape, no text or texture, no Arch, no team
// marks. Food hexes: toasted ravioli #C98A3A and #E0A44E, cup #F4F1EA, marinara #C2361F, crust #D9A45A, Provel #F3E3B5, burnt end
// #4A2A1C, bark #6B3A22, butcher paper #E8DCC4.
//   A  two toasted ravioli and a cup of marinara
//   B  a round St. Louis-style pizza, cut in squares (the party cut)
//   C  burnt ends on butcher paper
// Usage, from mo-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let NAVY: UInt32 = 0x0A3161, RAV1: UInt32 = 0xC98A3A, RAV2: UInt32 = 0xE0A44E, CUP: UInt32 = 0xF4F1EA, SAUCE: UInt32 = 0xC2361F
let CRUST: UInt32 = 0xD9A45A, PROVEL: UInt32 = 0xF3E3B5, BURNT: UInt32 = 0x4A2A1C, BARK: UInt32 = 0x6B3A22, PAPER: UInt32 = 0xE8DCC4

/// A: two toasted ravioli and a cup of marinara. CoreGraphics y-up, s = canvas size. Identical to make-brand.swift's ravioli().
func ravioli(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
        CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
    }
    c.setFillColor(rgb(RAV1)); c.addPath(R(0.135, 0.35, 0.34, 0.34, 0.06)); c.fillPath()
    c.setFillColor(rgb(RAV2)); c.addPath(R(0.405, 0.35, 0.34, 0.34, 0.06)); c.fillPath()
    c.setFillColor(rgb(CUP)); c.fillEllipse(in: CGRect(x: 0.645 * s, y: 0.29 * s, width: 0.22 * s, height: 0.22 * s))
    c.setFillColor(rgb(SAUCE)); c.fillEllipse(in: CGRect(x: 0.67 * s, y: 0.315 * s, width: 0.17 * s, height: 0.17 * s))
}

/// B: a St. Louis-style pizza from above, cut in squares.
func pizza(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(CRUST)); c.fillEllipse(in: CGRect(x: 0.15 * s, y: 0.15 * s, width: 0.70 * s, height: 0.70 * s))
    c.setFillColor(rgb(PROVEL)); c.fillEllipse(in: CGRect(x: 0.27 * s, y: 0.27 * s, width: 0.46 * s, height: 0.46 * s))
    c.setFillColor(rgb(CRUST))
    for k in 1...3 {
        let t = 0.27 + 0.46 * CGFloat(k) / 4
        c.fill(CGRect(x: t * s - 0.006 * s, y: 0.27 * s, width: 0.012 * s, height: 0.46 * s))
        c.fill(CGRect(x: 0.27 * s, y: t * s - 0.006 * s, width: 0.46 * s, height: 0.012 * s))
    }
}

/// C: burnt ends on butcher paper.
func burntEnds(_ c: CGContext, _ s: CGFloat) {
    c.setFillColor(rgb(PAPER)); c.fill(CGRect(x: 0.14 * s, y: 0.30 * s, width: 0.72 * s, height: 0.40 * s))
    for (i, (x, y)) in [(0.24, 0.42), (0.42, 0.48), (0.58, 0.40), (0.34, 0.55)].enumerated() {
        c.setFillColor(rgb(i % 2 == 0 ? BURNT : BARK))
        c.addPath(CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: 0.17 * s, height: 0.15 * s), cornerWidth: 0.03 * s, cornerHeight: 0.03 * s, transform: nil)); c.fillPath()
    }
}

func render(_ n: Int, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(NAVY)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", ravioli)
render(1024, out + "/concept-b-1024.png", pizza)
render(1024, out + "/concept-c-1024.png", burntEnds)

import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, kcbbq, toasted, stlclassics, cashew, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // downtown St. Louis (the Old Courthouse), so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 38.6255, longitude: -90.1890)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("Arthur Bryant's Barbecue", "Kansas City"), pick("Leong's Asian Diner", "Springfield"), pick("Ted Drewes Frozen Custard", "St. Louis")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "kcbbq":
            // 18th and Vine, Kansas City
            model.screenshotLocation = CLLocation(latitude: 39.0911, longitude: -94.5619)
            open(.kcbbq)
        case "toasted":
            // The Hill
            model.screenshotLocation = CLLocation(latitude: 38.6168, longitude: -90.2762)
            open(.toasted)
        case "stlclassics": open(.stlclassics)
        case "cashew":
            // downtown Springfield
            model.screenshotLocation = CLLocation(latitude: 37.2090, longitude: -93.2923)
            open(.cashew)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // Charlie Gitto's on The Hill, with its toasted ravioli note
            open(.toasted)
            if let p = pick("Charlie Gitto's On the Hill", "St. Louis") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("Gioia's Deli", "St. Louis")
        case "kcbbq": pick("Arthur Bryant's Barbecue", "Kansas City")
        case "toasted": pick("Charlie Gitto's On the Hill", "St. Louis")
        case "stlclassics": pick("Ted Drewes Frozen Custard", "St. Louis")
        case "cashew": pick("Leong's Asian Diner", "Springfield")
        case "map": pick("Gioia's Deli", "St. Louis")
        case "honors": pick("Balkan Treat Box", "Webster Groves")
        case "oldest": pick("J Huston Tavern", "Arrow Rock")
        case "saved": pick("Arthur Bryant's Barbecue", "Kansas City")
        case "about": nil
        default: pick("Charlie Gitto's On the Hill", "St. Louis")
        }
        model.selectedPlace = place
    }
}

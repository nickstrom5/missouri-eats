import CoreLocation
import Observation
import UIKit

/// "Near me" sorting. Asks for when-in-use permission only when a list is sorted by distance or "My location" is tapped; the location never leaves the device.
@MainActor
@Observable
final class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private(set) var location: CLLocation?
    private(set) var status: CLAuthorizationStatus = .notDetermined
    /// no fix within 12 seconds, or Core Location reported an error
    private(set) var failed = false
    private var timeout: Task<Void, Never>?
    /// when the current request started: a fix from before it is a cached one (from launch, or before a drive) and doesn't count
    private var askedAt = Date.distantPast

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        status = manager.authorizationStatus
    }

    var isDenied: Bool { status == .denied || status == .restricted }

    /// Every place is in Missouri, so a reader elsewhere (an App Reviewer in California, say) gets told rather than an empty map.
    /// A coarse outline of the state (Idaho's lesson: a bounding box would count East St. Louis, Kansas City, Kansas and Cairo),
    /// drawn a little outside the line so the river shores count as inside.
    var isOutsideMissouri: Bool {
        guard let c = location?.coordinate else { return false }
        return !MissouriOutline.contains(c)
    }

    /// Once location is off for the app, iOS won't ask again; the app's page in Settings is the only way back.
    static func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) }
    }

    func request() {
        switch manager.authorizationStatus {
        case .notDetermined: manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways: locate()
        default: break
        }
    }

    private func locate() {
        failed = false
        let asked = Date()
        askedAt = asked
        manager.requestLocation()
        timeout?.cancel()
        timeout = Task { [weak self] in
            try? await Task.sleep(for: .seconds(12))
            guard let self, !Task.isCancelled else { return }
            if (self.location?.timestamp ?? .distantPast) < asked { self.failed = true }
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        let s = m.authorizationStatus
        Task { @MainActor in
            self.status = s
            if s == .authorizedWhenInUse || s == .authorizedAlways { self.locate() }
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let l = locations.last else { return }
        Task { @MainActor in
            // "My location" needs a fresh fix on every tap: a cached one from before the request would put you back where you were
            guard l.timestamp >= self.askedAt.addingTimeInterval(-2) else { return }
            self.location = l; self.failed = false; self.timeout?.cancel()
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in if self.location == nil { self.failed = true } }
    }
}

extension CLLocation {
    /// "0.4 mi", "12 mi", "1,012 mi" (an App Reviewer in California is a thousand miles out)
    func milesText(to other: CLLocation) -> String {
        let mi = distance(from: other) / 1609.344
        return (mi < 10 ? mi.formatted(.number.precision(.fractionLength(1))) : Int(mi.rounded()).formatted()) + " mi"
    }
}

/// A coarse Missouri outline (longitude, latitude), about 400 m outside the Overture land outline but never over a neighbour's land
/// (buffer 0.004°, minus the neighbours buffered 0.0015°, simplify 0.006°). St. Louis, Kansas City, St. Joseph, Hannibal, Cape Girardeau,
/// Joplin, Branson and the Bootheel (Kennett, Hayti) are inside; East St. Louis, Quincy and Cairo (Illinois), Kansas City, Elwood and
/// Pittsburg (Kansas), Blytheville and Bentonville (Arkansas) and Keokuk (Iowa) are not.
enum MissouriOutline {
    static let rings: [[(Double, Double)]] = [
        [(-94.616, 36.501), (-94.607, 39.117), (-94.589, 39.137), (-94.588, 39.153), (-94.609, 39.163), (-94.653, 39.156),
         (-94.66, 39.179), (-94.678, 39.186), (-94.741, 39.172), (-94.763, 39.182), (-94.782, 39.208), (-94.826, 39.213),
         (-94.833, 39.221), (-94.824, 39.242), (-94.831, 39.258), (-94.884, 39.286), (-94.905, 39.314), (-94.908, 39.353),
         (-94.881, 39.37), (-94.883, 39.389), (-94.896, 39.395), (-94.939, 39.389), (-94.948, 39.411), (-94.971, 39.422),
         (-94.987, 39.446), (-95.04, 39.468), (-95.053, 39.503), (-95.109, 39.545), (-95.103, 39.576), (-95.065, 39.575),
         (-95.049, 39.587), (-95.053, 39.627), (-95.026, 39.665), (-94.972, 39.684), (-94.962, 39.741), (-94.945, 39.743),
         (-94.896, 39.723), (-94.861, 39.741), (-94.857, 39.759), (-94.87, 39.775), (-94.911, 39.759), (-94.935, 39.775),
         (-94.928, 39.788), (-94.885, 39.792), (-94.875, 39.809), (-94.886, 39.834), (-94.916, 39.838), (-94.939, 39.853),
         (-94.928, 39.89), (-94.951, 39.902), (-95.006, 39.902), (-95.025, 39.893), (-95.036, 39.867), (-95.082, 39.863),
         (-95.128, 39.875), (-95.147, 39.906), (-95.202, 39.906), (-95.204, 39.94), (-95.247, 39.949), (-95.304, 39.988),
         (-95.315, 40.013), (-95.353, 40.032), (-95.389, 40.028), (-95.41, 40.037), (-95.419, 40.061), (-95.392, 40.119),
         (-95.426, 40.135), (-95.435, 40.16), (-95.478, 40.187), (-95.481, 40.2), (-95.468, 40.225), (-95.475, 40.242),
         (-95.55, 40.262), (-95.551, 40.289), (-95.563, 40.299), (-95.611, 40.315), (-95.655, 40.312), (-95.653, 40.321),
         (-95.624, 40.333), (-95.622, 40.347), (-95.659, 40.413), (-95.656, 40.44), (-95.693, 40.473), (-95.697, 40.504),
         (-95.661, 40.516), (-95.654, 40.547), (-95.679, 40.564), (-95.695, 40.558), (-95.697, 40.533), (-95.708, 40.523),
         (-95.759, 40.528), (-95.773, 40.574), (-95.766, 40.584), (-94.295, 40.57), (-92.687, 40.588), (-91.73, 40.612),
         (-91.688, 40.58), (-91.689, 40.556), (-91.621, 40.54), (-91.622, 40.508), (-91.592, 40.491), (-91.575, 40.464),
         (-91.526, 40.457), (-91.535, 40.438), (-91.521, 40.433), (-91.525, 40.41), (-91.499, 40.399), (-91.483, 40.404),
         (-91.494, 40.396), (-91.482, 40.38), (-91.465, 40.385), (-91.467, 40.376), (-91.454, 40.374), (-91.441, 40.385),
         (-91.422, 40.378), (-91.463, 40.343), (-91.491, 40.287), (-91.492, 40.26), (-91.508, 40.237), (-91.513, 40.137),
         (-91.491, 40.057), (-91.496, 40.036), (-91.421, 39.927), (-91.445, 39.894), (-91.448, 39.87), (-91.434, 39.839),
         (-91.379, 39.81), (-91.365, 39.792), (-91.371, 39.732), (-91.277, 39.665), (-91.23, 39.62), (-91.183, 39.602),
         (-91.155, 39.547), (-91.101, 39.537), (-91.039, 39.447), (-90.942, 39.403), (-90.931, 39.387), (-90.795, 39.309),
         (-90.759, 39.268), (-90.732, 39.255), (-90.711, 39.154), (-90.682, 39.097), (-90.716, 39.052), (-90.68, 38.991),
         (-90.662, 38.924), (-90.62, 38.885), (-90.584, 38.868), (-90.558, 38.868), (-90.501, 38.907), (-90.469, 38.96),
         (-90.41, 38.962), (-90.309, 38.923), (-90.251, 38.918), (-90.11, 38.846), (-90.123, 38.801), (-90.157, 38.78),
         (-90.211, 38.726), (-90.211, 38.702), (-90.183, 38.66), (-90.186, 38.612), (-90.253, 38.542), (-90.291, 38.433),
         (-90.344, 38.387), (-90.37, 38.34), (-90.373, 38.279), (-90.352, 38.211), (-90.322, 38.18), (-90.277, 38.157),
         (-90.218, 38.092), (-90.174, 38.068), (-90.131, 38.061), (-90.001, 37.963), (-89.942, 37.969), (-89.926, 37.958),
         (-89.976, 37.927), (-89.949, 37.879), (-89.9, 37.869), (-89.841, 37.903), (-89.8, 37.88), (-89.799, 37.861),
         (-89.787, 37.85), (-89.741, 37.845), (-89.67, 37.798), (-89.662, 37.786), (-89.664, 37.749), (-89.617, 37.748),
         (-89.574, 37.708), (-89.518, 37.691), (-89.518, 37.639), (-89.477, 37.593), (-89.488, 37.582), (-89.521, 37.584),
         (-89.518, 37.536), (-89.487, 37.484), (-89.439, 37.433), (-89.422, 37.386), (-89.435, 37.347), (-89.491, 37.333),
         (-89.513, 37.312), (-89.522, 37.283), (-89.501, 37.251), (-89.46, 37.248), (-89.469, 37.22), (-89.463, 37.197),
         (-89.425, 37.135), (-89.381, 37.095), (-89.387, 37.056), (-89.38, 37.038), (-89.28, 36.987), (-89.262, 36.998),
         (-89.257, 37.02), (-89.304, 37.05), (-89.307, 37.068), (-89.26, 37.063), (-89.255, 37.069), (-89.237, 37.039),
         (-89.202, 37.015), (-89.188, 36.974), (-89.168, 36.969), (-89.125, 36.982), (-89.101, 36.961), (-89.119, 36.888),
         (-89.139, 36.849), (-89.171, 36.843), (-89.18, 36.831), (-89.172, 36.797), (-89.124, 36.784), (-89.118, 36.768),
         (-89.127, 36.753), (-89.169, 36.761), (-89.199, 36.74), (-89.201, 36.715), (-89.171, 36.688), (-89.173, 36.672),
         (-89.161, 36.666), (-89.199, 36.63), (-89.218, 36.577), (-89.261, 36.567), (-89.324, 36.632), (-89.366, 36.626),
         (-89.422, 36.495), (-89.465, 36.459), (-89.492, 36.474), (-89.464, 36.53), (-89.478, 36.569), (-89.543, 36.582),
         (-89.568, 36.565), (-89.573, 36.547), (-89.562, 36.525), (-89.521, 36.475), (-89.547, 36.427), (-89.511, 36.374),
         (-89.532, 36.341), (-89.606, 36.344), (-89.622, 36.323), (-89.579, 36.287), (-89.54, 36.276), (-89.536, 36.253),
         (-89.602, 36.24), (-89.695, 36.254), (-89.705, 36.244), (-89.694, 36.224), (-89.608, 36.17), (-89.593, 36.144),
         (-89.603, 36.121), (-89.68, 36.086), (-89.69, 36.03), (-89.708, 36.002), (-90.376, 35.997), (-90.336, 36.046),
         (-90.332, 36.066), (-90.319, 36.071), (-90.318, 36.089), (-90.299, 36.097), (-90.293, 36.113), (-90.272, 36.115),
         (-90.235, 36.138), (-90.22, 36.183), (-90.125, 36.228), (-90.129, 36.241), (-90.114, 36.264), (-90.083, 36.271),
         (-90.063, 36.302), (-90.08, 36.322), (-90.062, 36.384), (-90.08, 36.402), (-90.109, 36.405), (-90.143, 36.425),
         (-90.132, 36.454), (-90.142, 36.476), (-90.158, 36.481), (-90.152, 36.499), (-94.616, 36.501)],
        [(-90.15, 36.469), (-90.146, 36.464), (-90.154, 36.465), (-90.15, 36.469)]]

    static func contains(_ c: CLLocationCoordinate2D) -> Bool { rings.contains { contains(c, ring: $0) } }

    /// Ray casting: a point is inside when a ray east of it crosses the outline an odd number of times.
    static func contains(_ c: CLLocationCoordinate2D, ring: [(Double, Double)]) -> Bool {
        var inside = false
        var j = ring.count - 1
        for i in 0..<ring.count {
            let (xi, yi) = ring[i], (xj, yj) = ring[j]
            if (yi > c.latitude) != (yj > c.latitude) && c.longitude < (xj - xi) * (c.latitude - yi) / (yj - yi) + xi { inside.toggle() }
            j = i
        }
        return inside
    }
}

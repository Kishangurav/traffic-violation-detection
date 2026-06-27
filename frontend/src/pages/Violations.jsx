import { useEffect, useState } from "react"
import axios from "axios"

export default function Violations() {
  const [violations, setViolations] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState("all")

  useEffect(() => {
    fetchViolations()
    const interval = setInterval(fetchViolations, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchViolations = async () => {
    try {
      const res = await axios.get("/api/v1/violations")
      setViolations(res.data)
      setLoading(false)
    } catch (err) {
      console.error("API error:", err)
      setLoading(false)
    }
  }

  const deleteViolation = async (id) => {
    try {
      await axios.delete(`/api/v1/violations/${id}`)
      fetchViolations()
    } catch (err) {
      console.error("Delete error:", err)
    }
  }

  const filtered = filter === "all"
    ? violations
    : violations.filter(v => v.violation_type === filter)

  const badgeColor = (type) => {
    if (type === "red_light") return "bg-red-500"
    if (type === "speeding") return "bg-yellow-500"
    if (type === "no_helmet") return "bg-blue-500"
    return "bg-gray-500"
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Violations</h2>
        <span className="text-sm text-gray-400">{filtered.length} records</span>
      </div>

      {/* Filter buttons */}
      <div className="flex gap-3 mb-6">
        {["all", "red_light", "speeding", "no_helmet"].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition
              ${filter === f
                ? "bg-red-500 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}
          >
            {f === "all" ? "All" : f === "red_light" ? "Red Light" : f === "speeding" ? "Speeding" : "No Helmet"}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-gray-400">Loading violations...</p>
      ) : filtered.length === 0 ? (
        <div className="bg-gray-900 rounded-xl p-8 text-center border border-gray-800">
          <p className="text-gray-400">No violations found</p>
          <p className="text-xs text-gray-600 mt-1">Run main.py to start detecting violations</p>
        </div>
      ) : (
        <div className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400 text-xs uppercase">
                <th className="text-left px-4 py-3">Vehicle ID</th>
                <th className="text-left px-4 py-3">Type</th>
                <th className="text-left px-4 py-3">Plate</th>
                <th className="text-left px-4 py-3">Speed</th>
                <th className="text-left px-4 py-3">Timestamp</th>
                <th className="text-left px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((v, i) => (
                <tr key={i} className="border-b border-gray-800 hover:bg-gray-800 transition">
                  <td className="px-4 py-3 font-mono text-yellow-400">#{v.vehicle_id}</td>
                  <td className="px-4 py-3">
                    <span className={`${badgeColor(v.violation_type)} text-white text-xs px-2 py-1 rounded-full`}>
                      {v.violation_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-300">{v.plate_number || "Unknown"}</td>
                  <td className="px-4 py-3 text-gray-300">{v.speed ? `${v.speed} km/h` : "—"}</td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{v.timestamp}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => deleteViolation(v.vehicle_id)}
                      className="text-xs text-red-400 hover:text-red-300 transition"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
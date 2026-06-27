import { useEffect, useState } from "react"
import axios from "axios"

export default function Cameras() {
  const [cameras, setCameras] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    camera_id: "",
    name: "",
    location: "",
    video_source: "",
    stop_line_y: 300,
    speed_limit: 50,
    status: "active"
  })

  useEffect(() => {
    fetchCameras()
  }, [])

  const fetchCameras = async () => {
    try {
      const res = await axios.get("/api/v1/cameras")
      setCameras(res.data)
      setLoading(false)
    } catch (err) {
      console.error("API error:", err)
      setLoading(false)
    }
  }

  const addCamera = async () => {
    try {
      await axios.post("/api/v1/cameras", {
        ...form,
        camera_id: parseInt(form.camera_id),
        stop_line_y: parseInt(form.stop_line_y),
        speed_limit: parseInt(form.speed_limit)
      })
      setShowForm(false)
      fetchCameras()
    } catch (err) {
      console.error("Add camera error:", err)
    }
  }

  const deleteCamera = async (id) => {
    try {
      await axios.delete(`/api/v1/cameras/${id}`)
      fetchCameras()
    } catch (err) {
      console.error("Delete error:", err)
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Cameras</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-red-500 hover:bg-red-600 text-white text-sm px-4 py-2 rounded-lg transition"
        >
          + Add Camera
        </button>
      </div>

      {/* Add Camera Form */}
      {showForm && (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-6">
          <h3 className="text-sm font-semibold text-gray-400 mb-4">New Camera</h3>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Camera ID", key: "camera_id" },
              { label: "Name", key: "name" },
              { label: "Location", key: "location" },
              { label: "Video Source", key: "video_source" },
              { label: "Stop Line Y", key: "stop_line_y" },
              { label: "Speed Limit (km/h)", key: "speed_limit" },
            ].map(({ label, key }) => (
              <div key={key}>
                <label className="text-xs text-gray-400 mb-1 block">{label}</label>
                <input
                  value={form[key]}
                  onChange={e => setForm({ ...form, [key]: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-red-500"
                />
              </div>
            ))}
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={addCamera}
              className="bg-red-500 hover:bg-red-600 text-white text-sm px-4 py-2 rounded-lg transition"
            >
              Save Camera
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="bg-gray-700 hover:bg-gray-600 text-white text-sm px-4 py-2 rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Camera Cards */}
      {loading ? (
        <p className="text-gray-400">Loading cameras...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cameras.map((cam, i) => (
            <div key={i} className="bg-gray-900 rounded-xl p-5 border border-gray-800">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${cam.status === "active" ? "bg-green-500 animate-pulse" : "bg-gray-500"}`}></div>
                  <h3 className="font-semibold text-white">{cam.name}</h3>
                </div>
                <button
                  onClick={() => deleteCamera(cam.camera_id)}
                  className="text-xs text-red-400 hover:text-red-300 transition"
                >
                  Remove
                </button>
              </div>
              <div className="space-y-1 text-sm text-gray-400">
                <p>📍 {cam.location}</p>
                <p>🎥 {cam.video_source}</p>
                <p>🛑 Stop line: y={cam.stop_line_y}</p>
                <p>⚡ Speed limit: {cam.speed_limit} km/h</p>
              </div>
              <div className="mt-3">
                <span className={`text-xs px-2 py-1 rounded-full ${cam.status === "active" ? "bg-green-900 text-green-400" : "bg-gray-700 text-gray-400"}`}>
                  {cam.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
import { useEffect, useState } from "react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts"

const COLORS = ["#E24B4A", "#F59E0B", "#3B82F6"]

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const res = await axios.get("/api/v1/stats")
      setStats(res.data)
      setLoading(false)
    } catch (err) {
      console.error("API error:", err)
      setLoading(false)
    }
  }

  const chartData = stats ? [
    { name: "Red Light", value: stats.red_light_violations },
    { name: "Speeding", value: stats.speeding_violations },
    { name: "No Helmet", value: stats.helmet_violations },
  ] : []

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Live Dashboard</h2>

      {loading ? (
        <p className="text-gray-400">Loading stats...</p>
      ) : (
        <>
          {/* Stat Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard title="Total Violations" value={stats?.total_violations} color="red" />
            <StatCard title="Red Light" value={stats?.red_light_violations} color="orange" />
            <StatCard title="Speeding" value={stats?.speeding_violations} color="yellow" />
            <StatCard title="No Helmet" value={stats?.helmet_violations} color="blue" />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Bar Chart */}
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <h3 className="text-sm font-semibold text-gray-400 mb-4">Violations by Type</h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData}>
                  <XAxis dataKey="name" tick={{ fill: "#9CA3AF", fontSize: 12 }} />
                  <YAxis tick={{ fill: "#9CA3AF", fontSize: 12 }} />
                  <Tooltip contentStyle={{ background: "#1F2937", border: "none" }} />
                  <Bar dataKey="value" fill="#E24B4A" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Pie Chart */}
            <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
              <h3 className="text-sm font-semibold text-gray-400 mb-4">Violation Distribution</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {chartData.map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1F2937", border: "none" }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex justify-center gap-4 mt-2">
                {chartData.map((item, i) => (
                  <div key={i} className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded-full" style={{ background: COLORS[i] }}></div>
                    <span className="text-xs text-gray-400">{item.name}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* API Status */}
          <div className="mt-6 bg-gray-900 rounded-xl p-4 border border-gray-800">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <span className="text-sm text-gray-400">API Connected — Auto refreshing every 5 seconds</span>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

function StatCard({ title, value, color }) {
  const colors = {
    red: "border-red-500 text-red-400",
    orange: "border-orange-500 text-orange-400",
    yellow: "border-yellow-500 text-yellow-400",
    blue: "border-blue-500 text-blue-400",
  }
  return (
    <div className={`bg-gray-900 rounded-xl p-4 border-l-4 ${colors[color]} border border-gray-800`}>
      <p className="text-xs text-gray-400 mb-1">{title}</p>
      <p className={`text-3xl font-bold ${colors[color]}`}>{value ?? 0}</p>
    </div>
  )
}
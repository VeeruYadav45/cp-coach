import { useEffect, useState } from 'react'
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts'

type SkillScore = {
  tag: string
  attempted: number
  solved: number
  accuracy: number
  score: number
}

function App() {
  const [skills, setSkills] = useState<SkillScore[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://localhost:8000/score/Yakurto')
      .then((res) => res.json())
      .then((data) => {
        setSkills(data.scores || [])
        setLoading(false)
      })
      .catch((err) => {
        console.error('Error fetching scores:', err)
        setLoading(false)
      })
  }, [])

  if (loading) return <div style={{ padding: 24 }}>Loading skills...</div>

  // Take top 8 most attempted or highest scored topics for a clean radar chart
  const radarData = skills.slice(0, 8).map((s) => ({
    tag: s.tag,
    score: s.score,
  }))

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      <h1>CP Coach</h1>
      <p style={{ color: '#666' }}>Skill breakdown for <strong>Yakurto</strong></p>

      {/* Radar Chart Section */}
      <div style={{ width: '100%', height: 350, margin: '20px 0' }}>
        <h3>Skill Radar (Top Topics)</h3>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="tag" tick={{ fontSize: 12 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar
              name="Skill Score"
              dataKey="score"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.5}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Ranked Skill List */}
      <h3 style={{ marginTop: 40 }}>All Topic Scores</h3>
      <div style={{ display: 'grid', gap: 12 }}>
        {skills.map((s) => (
          <div
            key={s.tag}
            style={{
              border: '1px solid #e5e7eb',
              borderRadius: 8,
              padding: '12px 16px',
              display: 'flex',
              flexDirection: 'column',
              gap: 8,
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>{s.tag}</span>
              <span style={{ fontWeight: 700, color: '#2563eb' }}>
                Score: {s.score} / 100
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, color: '#555' }}>
              <span>Accuracy: {s.accuracy}%</span>
              <span>Solved: {s.solved} / {s.attempted}</span>
            </div>

            {/* Score progress bar */}
            <div style={{ background: '#f3f4f6', height: 8, borderRadius: 4, overflow: 'hidden' }}>
              <div
                style={{
                  background: s.score >= 70 ? '#10b981' : s.score >= 40 ? '#f59e0b' : '#ef4444',
                  width: `${s.score}%`,
                  height: '100%',
                  borderRadius: 4,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App

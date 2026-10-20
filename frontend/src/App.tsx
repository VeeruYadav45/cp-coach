import { useEffect, useState, type FormEvent } from 'react'
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

type Recommendation = {
  id: number
  contest_id: number
  problem_index: string
  name: string
  rating: number
  tags: string[]
  url: string
  match_score: number
  reason: string
}

function App() {
  const [handle, setHandle] = useState('Yakurto')
  const [inputHandle, setInputHandle] = useState('Yakurto')
  const [skills, setSkills] = useState<SkillScore[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [userRating, setUserRating] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchUserData = (targetHandle: string) => {
    setLoading(true)
    setError(null)

    Promise.all([
      fetch(`http://localhost:8000/score/${targetHandle}`).then(async (res) => {
        if (!res.ok) throw new Error(`User '${targetHandle}' not found on Codeforces.`)
        return res.json()
      }),
      fetch(`http://localhost:8000/recommend/${targetHandle}`).then((res) => res.json()),
    ])
      .then(([scoreData, recData]) => {
        setSkills(scoreData.scores || [])
        setRecommendations(recData.recommendations || [])
        setUserRating(recData.user_rating || null)
        setHandle(targetHandle)
        setLoading(false)
      })
      .catch((err) => {
        console.error(err)
        setError(err.message || 'Failed to fetch user data.')
        setLoading(false)
      })
  }

  // Load Yakurto initially on startup
  useEffect(() => {
    fetchUserData('Yakurto')
  }, [])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const trimmed = inputHandle.trim()
    if (trimmed) {
      fetchUserData(trimmed)
    }
  }

  const radarData = skills.slice(0, 8).map((s) => ({
    tag: s.tag,
    score: s.score,
  }))

  return (
    <div style={{ maxWidth: 950, margin: '0 auto', padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      {/* Top Header & Search Bar */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16, marginBottom: 24 }}>
        <div>
          <h1 style={{ margin: 0 }}>CP Coach</h1>
          <p style={{ margin: '4px 0', color: '#666' }}>Personalized training for <strong>{handle}</strong></p>
        </div>

        {/* Handle Search Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <input
            type="text"
            value={inputHandle}
            onChange={(e) => setInputHandle(e.target.value)}
            placeholder="Enter Codeforces handle..."
            style={{
              padding: '8px 14px',
              border: '1px solid #d1d5db',
              borderRadius: 6,
              fontSize: 14,
              outline: 'none',
              width: 200,
            }}
          />
          <button
            type="submit"
            disabled={loading}
            style={{
              background: '#2563eb',
              color: '#fff',
              border: 'none',
              padding: '8px 16px',
              borderRadius: 6,
              fontSize: 14,
              fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </form>

        {userRating && !loading && (
          <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', padding: '6px 14px', borderRadius: 8 }}>
            <span style={{ fontSize: 12, color: '#1e40af', fontWeight: 600 }}>CF Rating: </span>
            <strong style={{ fontSize: 16, color: '#1d4ed8' }}>{userRating}</strong>
          </div>
        )}
      </header>

      {/* Error Message */}
      {error && (
        <div style={{ background: '#fee2e2', border: '1px solid #f87171', color: '#991b1b', padding: 12, borderRadius: 8, marginBottom: 20 }}>
          ⚠️ {error}
        </div>
      )}

      {/* Loading Indicator */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#4b5563' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>🔄</div>
          <strong>Fetching Codeforces submissions & analyzing {inputHandle}...</strong>
          <p style={{ fontSize: 13, color: '#6b7280' }}>If this is a new handle, we are syncing with Codeforces API (takes ~2 seconds).</p>
        </div>
      ) : (
        <>
          {/* Recommended Practice Problems Section */}
          <section style={{ marginBottom: 40 }}>
            <h2 style={{ fontSize: 20, color: '#111827', marginBottom: 16 }}>🎯 Recommended Practice</h2>
            <div style={{ display: 'grid', gap: 14 }}>
              {recommendations.length === 0 ? (
                <p style={{ color: '#6b7280' }}>No recommendations found.</p>
              ) : (
                recommendations.map((rec) => (
                  <div
                    key={rec.id}
                    style={{
                      border: '1px solid #e5e7eb',
                      borderRadius: 10,
                      padding: '16px 20px',
                      background: '#ffffff',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      flexWrap: 'wrap',
                      gap: 12,
                    }}
                  >
                    <div style={{ flex: '1 1 300px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <span style={{ fontWeight: 700, fontSize: 16 }}>{rec.name}</span>
                        <span style={{
                          background: '#fef3c7',
                          color: '#92400e',
                          padding: '2px 8px',
                          borderRadius: 6,
                          fontSize: 12,
                          fontWeight: 600
                        }}>
                          {rec.rating}
                        </span>
                      </div>
                      <p style={{ margin: '6px 0', fontSize: 13, color: '#059669', fontWeight: 500 }}>
                        💡 {rec.reason}
                      </p>
                      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                        {rec.tags.map((t) => (
                          <span
                            key={t}
                            style={{
                              background: '#f3f4f6',
                              color: '#4b5563',
                              fontSize: 11,
                              padding: '2px 8px',
                              borderRadius: 4,
                            }}
                          >
                            #{t}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <a
                        href={rec.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-block',
                          background: '#2563eb',
                          color: '#ffffff',
                          padding: '8px 16px',
                          borderRadius: 6,
                          textDecoration: 'none',
                          fontWeight: 600,
                          fontSize: 14,
                        }}
                      >
                        Solve on CF ↗
                      </a>
                    </div>
                  </div>
                ))
              )}
            </div>
          </section>

          {/* Radar Chart Section */}
          <section style={{ marginBottom: 40 }}>
            <h2 style={{ fontSize: 20, color: '#111827', marginBottom: 12 }}>Skill Radar (Top Topics)</h2>
            <div style={{ width: '100%', height: 350 }}>
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
          </section>

          {/* Ranked Skill List */}
          <section>
            <h2 style={{ fontSize: 20, color: '#111827', marginBottom: 16 }}>All Topic Scores</h2>
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
          </section>
        </>
      )}
    </div>
  )
}

export default App

import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [productName, setProductName] = useState('')
  const [reviewText, setReviewText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      // Pastikan backend berjalan di port 6543
      const res = await axios.get('http://localhost:6543/api/reviews')
      setHistory(res.data)
    } catch (err) {
      console.error("Gagal ambil history:", err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!productName || !reviewText) return alert("Isi semua data dulu ya!")

    setLoading(true)
    setResult(null)

    try {
      const res = await axios.post('http://localhost:6543/api/analyze-review', {
        product_name: productName,
        review_text: reviewText
      })
      setResult(res.data)
      fetchHistory()
    } catch (err) {
      alert("Gagal koneksi ke Backend. Cek terminal backend!")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getSentimentClass = (sentiment) => {
    if (!sentiment) return 'sentiment-neutral';
    const s = sentiment.toLowerCase();
    if (s.includes('positive')) return 'sentiment-positive';
    if (s.includes('negative')) return 'sentiment-negative';
    return 'sentiment-neutral';
  }

  return (
    <div className="container">
      {/* HEADER */}
      <div className="header">
        <h1>✨ AI Product Analyzer</h1>
        <p className="subtitle">Review Analyzer Powered by Hugging Face & Gemini</p>
      </div>
      
      {/* GLASS CARD (FORM) */}
      <div className="glass-card">
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>📦 Nama Produk</label>
            <input 
              type="text" 
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              placeholder="Contoh: Laptop Gaming ROG..."
            />
          </div>
          
          <div className="input-group">
            <label>💬 Ulasan Pembeli</label>
            <textarea 
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              placeholder="Paste ulasan di sini..."
            />
          </div>

          <button type="submit" className="btn-analyze" disabled={loading}>
            {loading ? 'Sedang Menganalisis... 🔮' : 'Analisis Sekarang 🚀'}
          </button>
        </form>

        {/* RESULT AREA */}
        {result && (
          <div className="result-box">
            <div className="result-header">
              <h3>🎯 Hasil Analisis</h3>
              <span className={`sentiment-badge ${getSentimentClass(result.sentiment)}`}>
                {result.sentiment}
              </span>
            </div>
            
            <p style={{marginBottom: '10px'}}>
              <strong>Tingkat Keyakinan AI:</strong> {(result.confidence * 100).toFixed(1)}%
            </p>

            <div className="key-points">
              <strong>💡 Poin-Poin Penting:</strong>
              <ul style={{marginTop: '5px'}}>
                {result.key_points && Array.isArray(result.key_points) && result.key_points.length > 0 ? (
                  result.key_points.map((point, idx) => (
                    <li key={idx}>{point}</li>
                    ))
                  ) : (
                    <li style={{color: 'yellow'}}>⚠️ Data poin penting tidak ditemukan/gagal diekstrak.</li>
                  )}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* HISTORY SECTION */}
      <div className="history-section">
        <h2 style={{ marginBottom: '20px', fontSize: '1.5rem' }}>📜 Riwayat Analisis</h2>
        
        {history.length === 0 ? (
          <p style={{ opacity: 0.6, fontStyle: 'italic' }}>Belum ada data tersimpan.</p>
        ) : (
          <div className="history-grid">
            {history.map((item) => (
              <div key={item.id} className="history-item">
                <div className="history-header">
                  <span className="product-title">{item.product_name}</span>
                  <span className={`sentiment-badge ${getSentimentClass(item.sentiment)}`} style={{fontSize:'0.7rem'}}>
                    {item.sentiment}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', color: '#cbd5e0' }}>
                  {/* BAGIAN INI SUDAH DIPERBAIKI (Hapus kode duplikat yang error) */}
                  <ul style={{ paddingLeft: '20px', margin: 0 }}>
                    {/* Menampilkan maksimal 2 poin saja agar rapi */}
                    {item.key_points && item.key_points.slice(0, 2).map((p, i) => (
                        <li key={i}>{p}</li>
                    ))}
                    {/* Jika lebih dari 2 poin, tampilkan "dan lainnya" */}
                    {item.key_points && item.key_points.length > 2 && (
                        <li style={{listStyle: 'none', opacity: 0.7}}>...dan lainnya</li>
                    )}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
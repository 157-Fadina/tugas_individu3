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
      const res = await axios.get('http://localhost:6543/api/reviews')
      setHistory(res.data)
    } catch (err) {
      console.error("Gagal ambil history:", err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!productName || !reviewText) return alert("Isi semua data!")

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
      alert("Gagal menganalisis. Cek backend!")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>Product Review Analyzer</h1>
      
      {/* --- FORM INPUT --- */}
      <div style={{ marginBottom: '30px', border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
        <h3>Analisis Review Baru</h3>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '10px' }}>
            <label>Nama Produk:</label><br/>
            <input 
              type="text" 
              value={productName}
              onChange={(e) => setProductName(e.target.value)}
              style={{ width: '100%', padding: '8px' }}
              placeholder="Contoh: Laptop Gaming X"
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Isi Review:</label><br/>
            <textarea 
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              style={{ width: '100%', height: '100px', padding: '8px' }}
              placeholder="Ketik ulasan di sini..."
            />
          </div>
          <button type="submit" disabled={loading} style={{ padding: '10px 20px', cursor: 'pointer' }}>
            {loading ? 'Sedang Menganalisis...' : 'Analyze Review'}
          </button>
        </form>
      </div>

      {/* --- HASIL ANALISIS --- */}
      {result && (
        <div style={{ marginBottom: '30px', backgroundColor: '#e6fffa', padding: '20px', borderRadius: '8px', border: '1px solid #4fd1c5' }}>
          <h2>Hasil Analisis:</h2>
          <p><strong>Sentimen:</strong> {result.sentiment} (Confidence: {result.confidence.toFixed(2)})</p>
          <div>
            <strong>Poin Penting (by Gemini):</strong>
            <ul>
              {result.key_points.map((point, idx) => (
                <li key={idx}>{point}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* --- HISTORY --- */}
      <hr />
      <h3>Riwayat Analisis</h3>
      {history.length === 0 ? <p>Belum ada data.</p> : (
        <table border="1" cellPadding="10" style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              <th>Produk</th>
              <th>Sentimen</th>
              <th>Key Points</th>
            </tr>
          </thead>
          <tbody>
            {history.map((item) => (
              <tr key={item.id}>
                <td>{item.product_name}</td>
                <td>{item.sentiment}</td>
                <td>
                  <ul style={{ paddingLeft: '20px', margin: 0 }}>
                    {item.key_points.slice(0, 2).map((p, i) => <li key={i}>{p}</li>)}
                    {item.key_points.length > 2 && <li>...</li>}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default App
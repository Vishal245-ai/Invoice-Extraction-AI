import { useEffect, useState } from "react";
import Upload from "./pages/Upload";
import Invoices from "./pages/Invoices";
import Dashboard from "./pages/Dashboard";
import { getInvoices } from "./services/api";

function App() {
  const [invoices, setInvoices] = useState([]);
  const [vendorSpend, setVendorSpend] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ----------------------------
  // Fetch Data
  // ----------------------------
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const inv = await getInvoices();
      const safeInvoices = Array.isArray(inv) ? inv : [];

      setInvoices(safeInvoices);

      // ----------------------------
      // Vendor Spend Calculation
      // ----------------------------
      const spend = {};

      safeInvoices.forEach((item) => {
        if (!item || item.is_duplicate) return;

        const vendor =
          typeof item.vendor_name === "string" && item.vendor_name.trim()
            ? item.vendor_name.trim()
            : "unknown";

        const total = Number(item.total) || 0;

        spend[vendor] = (spend[vendor] || 0) + total;
      });

      setVendorSpend(spend);

    } catch (err) {
      console.error("Fetch error:", err);
      setError("Failed to load invoices");
      setInvoices([]);
      setVendorSpend({});
    } finally {
      setLoading(false);
    }
  };

  // ----------------------------
  // Initial Load
  // ----------------------------
  useEffect(() => {
    fetchData();
  }, []);

  // ----------------------------
  // UI STATES
  // ----------------------------
  if (loading) {
    return (
      <div style={centerStyle}>
        <h2>⏳ Loading invoices...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div style={centerStyle}>
        <h2 style={{ color: "red" }}>{error}</h2>
        <button onClick={fetchData}>Retry</button>
      </div>
    );
  }

  // ----------------------------
  // MAIN UI
  // ----------------------------
  return (
    <div style={containerStyle}>
      <Dashboard invoices={invoices} vendorSpend={vendorSpend} />
      <Upload refresh={fetchData} />
      <Invoices invoices={invoices} refresh={fetchData} />
    </div>
  );
}

export default App;

// ----------------------------
// STYLES
// ----------------------------
const containerStyle = {
  padding: "20px",
  maxWidth: "1200px",
  margin: "0 auto",
};

const centerStyle = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "60vh",
  flexDirection: "column",
};
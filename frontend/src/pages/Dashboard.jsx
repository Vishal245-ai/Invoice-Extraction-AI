import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useMemo } from "react";

export default function Dashboard({ invoices = [] }) {
  const { totalInvoices, totalSpend, vendorData, productData } = useMemo(() => {
    const validInvoices = Array.isArray(invoices)
      ? invoices.filter((inv) => inv && !inv.is_duplicate)
      : [];

    const totalInvoicesCount = validInvoices.length;

    const spend = validInvoices.reduce((sum, inv) => {
      const value = Number(inv?.total) || 0;
      return sum + value;
    }, 0);

    const vendorSpend = {};
    validInvoices.forEach((inv) => {
      const vendor =
        typeof inv?.vendor_name === "string" && inv.vendor_name.trim()
          ? inv.vendor_name.trim()
          : "unknown";

      const total = Number(inv?.total) || 0;
      vendorSpend[vendor] = (vendorSpend[vendor] || 0) + total;
    });

    const vendorChartData = Object.entries(vendorSpend).map(([name, value]) => ({
      name,
      value,
    }));

    const productSpend = {};
    validInvoices.forEach((inv) => {
      if (!Array.isArray(inv?.line_items)) return;

      inv.line_items.forEach((item) => {
        const name =
          typeof item?.product_name === "string" && item.product_name.trim()
            ? item.product_name.trim()
            : null;

        if (!name) return;

        const price = Number(item?.price) || 0;
        const quantity = Number(item?.quantity) || 1;
        const value = price * quantity;

        if (value > 0) {
          productSpend[name] = (productSpend[name] || 0) + value;
        }
      });
    });

    const productChartData = Object.entries(productSpend).map(([name, value]) => ({
      name,
      value,
    }));

    return {
      totalInvoices: totalInvoicesCount,
      totalSpend: spend,
      vendorData: vendorChartData,
      productData: productChartData,
    };
  }, [invoices]);

  const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7f7f", "#00C49F"];

  return (
    <div style={{ width: "100%", minWidth: 0 }}>
      <h1 style={{ marginBottom: 16 }}>📊 Invoice AI Dashboard</h1>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "16px",
          margin: "20px 0",
        }}
      >
        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Total Invoices</h3>
          <p style={cardValueStyle}>{totalInvoices}</p>
        </div>

        <div style={cardStyle}>
          <h3 style={cardTitleStyle}>Total Spend</h3>
          <p style={cardValueStyle}>₹ {totalSpend}</p>
        </div>
      </div>

      <h2 style={{ marginTop: 24 }}>📊 Vendor Spend</h2>
      {vendorData.length === 0 ? (
        <p>No data available</p>
      ) : (
        <div style={chartWrapStyle}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={vendorData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" interval={0} angle={-15} textAnchor="end" height={60} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <h2 style={{ marginTop: 24 }}>🥧 Product Spend</h2>
      {productData.length === 0 ? (
        <p>No data available</p>
      ) : (
        <div style={chartWrapStyle}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={productData}
                dataKey="value"
                nameKey="name"
                outerRadius={100}
                label
              >
                {productData.map((entry, index) => (
                  <Cell key={entry.name || index} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Legend />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

const cardStyle = {
  background: "#1e293b",
  padding: "20px",
  borderRadius: "12px",
  color: "white",
  minWidth: 0,
};

const cardTitleStyle = {
  margin: 0,
  fontSize: "14px",
  opacity: 0.85,
};

const cardValueStyle = {
  margin: "8px 0 0",
  fontSize: "28px",
  fontWeight: 700,
};

const chartWrapStyle = {
  width: "100%",
  height: 340,
  minWidth: 0,
  minHeight: 320,
};
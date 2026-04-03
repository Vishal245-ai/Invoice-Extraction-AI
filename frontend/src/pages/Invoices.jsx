import { useState } from "react";
import { deleteInvoice } from "../services/api";

export default function Invoices({ invoices = [], refresh }) {
  const [deletingId, setDeletingId] = useState(null);

  // ----------------------------
  // DELETE HANDLER
  // ----------------------------
  const handleDelete = async (id) => {
    if (!id) return;

    const confirmDelete = window.confirm("Delete this invoice?");
    if (!confirmDelete) return;

    try {
      setDeletingId(id);
      await deleteInvoice(id);
      await refresh?.();
    } catch (error) {
      console.error("Delete failed:", error);
      alert(error.message || "Delete failed");
    } finally {
      setDeletingId(null);
    }
  };

  // ----------------------------
  // PRODUCT HELPER
  // ----------------------------
  const getProductDetails = (line_items) => {
    if (!Array.isArray(line_items) || line_items.length === 0) {
      return { name: "N/A", qty: "-" };
    }

    const item = line_items.find(
      (i) =>
        i &&
        typeof i.product_name === "string" &&
        i.product_name.trim()
    );

    if (!item) return { name: "N/A", qty: "-" };

    return {
      name: item.product_name,
      qty: item.quantity || 1,
    };
  };

  return (
    <div style={{ marginTop: "30px" }}>
      <h2>📄 Invoices</h2>

      {/* TABLE WRAPPER (SCROLL FIX) */}
      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead style={theadStyle}>
            <tr>
              <th style={thStyle}>Vendor</th>
              <th style={thStyle}>Invoice No</th>
              <th style={thStyle}>Product</th>
              <th style={thStyle}>Qty</th>
              <th style={thStyle}>Total</th>
              <th style={thStyle}>Duplicate</th>
              <th style={thStyle}>Action</th>
            </tr>
          </thead>

          <tbody>
            {Array.isArray(invoices) && invoices.length > 0 ? (
              invoices.map((inv) => {
                if (!inv) return null;

                const vendor =
                  typeof inv.vendor_name === "string" &&
                  inv.vendor_name.trim()
                    ? inv.vendor_name
                    : "unknown";

                const total = Number(inv.total) || 0;
                const { name, qty } = getProductDetails(inv.line_items);

                return (
                  <tr key={inv.id} style={{ textAlign: "center" }}>
                    <td style={tdStyle}>{vendor}</td>
                    <td style={tdStyle}>{inv.invoice_number || "-"}</td>
                    <td style={tdStyle}>{name}</td>
                    <td style={tdStyle}>{qty}</td>
                    <td style={tdStyle}>₹ {total}</td>
                    <td style={tdStyle}>
                      {inv.is_duplicate ? "⚠️ Yes" : "No"}
                    </td>
                    <td style={tdStyle}>
                      <button
                        onClick={() => handleDelete(inv.id)}
                        disabled={deletingId === inv.id}
                        style={{
                          padding: "6px 10px",
                          borderRadius: "6px",
                          border: "none",
                          background:
                            deletingId === inv.id ? "#999" : "#ef4444",
                          color: "white",
                          cursor:
                            deletingId === inv.id
                              ? "not-allowed"
                              : "pointer",
                        }}
                      >
                        {deletingId === inv.id
                          ? "Deleting..."
                          : "Delete"}
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="7" style={{ padding: "20px" }}>
                  No invoices found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ----------------------------
// STYLES
// ----------------------------
const tableStyle = {
  width: "100%",
  borderCollapse: "collapse",
  marginTop: "10px",
  minWidth: "800px",
};

const theadStyle = {
  background: "#1e293b",
  color: "white",
};

const thStyle = {
  padding: "10px",
  border: "1px solid #ccc",
};

const tdStyle = {
  padding: "10px",
  border: "1px solid #ccc",
};
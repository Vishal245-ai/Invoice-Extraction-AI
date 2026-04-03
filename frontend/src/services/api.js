const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

// ----------------------------
// COMMON FETCH WRAPPER (SAFE)
// ----------------------------
const fetchWithTimeout = async (url, options = {}, timeout = 60000) => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(id);
    return res;
  } catch (error) {
    clearTimeout(id);

    if (error.name === "AbortError") {
      throw new Error("Request timeout. Please try again.");
    }

    throw new Error("Network error. Check backend connection.");
  }
};

// ----------------------------
// HANDLE RESPONSE
// ----------------------------
const handleResponse = async (res) => {
  let data = null;

  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const message =
      data?.detail || data?.message || `Error ${res.status}`;
    throw new Error(message);
  }

  return data;
};

// ----------------------------
// UPLOAD MULTIPLE INVOICES
// ----------------------------
export const uploadInvoices = async (files) => {
  if (!files || files.length === 0) {
    throw new Error("No files selected");
  }

  const formData = new FormData();

  Array.from(files).forEach((file) => {
    if (file) formData.append("files", file);
  });

  const res = await fetchWithTimeout(`${API}/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse(res);
};

// ----------------------------
// GET ALL INVOICES
// ----------------------------
export const getInvoices = async () => {
  const res = await fetchWithTimeout(`${API}/invoices`);

  const data = await handleResponse(res);

  return Array.isArray(data?.data) ? data.data : [];
};

// ----------------------------
// DELETE INVOICE
// ----------------------------
export const deleteInvoice = async (id) => {
  if (!id) throw new Error("Invalid invoice ID");

  const res = await fetchWithTimeout(`${API}/invoice/${id}`, {
    method: "DELETE",
  });

  return handleResponse(res);
};
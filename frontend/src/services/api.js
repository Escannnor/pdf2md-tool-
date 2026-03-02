import axios from "axios";

const API_BASE = "http://localhost:8000";

export const uploadPDF = async (file) => {
  const form = new FormData();
  form.append("file", file);
  const res = await axios.post(`${API_BASE}/upload_pdf`, form);
  return res.data;
};

export const extractText = async (data) => {
  const form = new FormData();
  for (let key in data) form.append(key, data[key]);
  const res = await axios.post(`${API_BASE}/extract_text`, form);
  return res.data;
};

export const extractContent = async (data) => {
  const form = new FormData();
  for (let key in data) form.append(key, data[key]);
  const res = await axios.post(`${API_BASE}/extract_content`, form);
  return res.data;
};

export const saveMarkdown = async ({ title, content }) => {
  const form = new FormData();
  if (title) form.append("title", title);
  form.append("content", content);
  const res = await axios.post(`${API_BASE}/save_markdown`, form);
  return res.data;
};

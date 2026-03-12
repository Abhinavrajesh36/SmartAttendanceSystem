const API = "http://localhost:8000";

export const registerUser = async (data) => {
    const res = await fetch(`${API}/api/register`, { method: "POST", body: data });
    return res.json();
};

export const markAttendance = async (data) => {
    const res = await fetch(`${API}/api/mark-attendance`, { method: "POST", body: data });
    return res.json();
};

/** Fetch all registered users. */
export const getUsers = async () => {
    const res = await fetch(`${API}/api/users`);
    if (!res.ok) throw new Error("Failed to fetch users");
    return res.json();
};

/**
 * Delete a user by their database ID.
 * Also removes them from the FAISS index on the backend.
 */
export const deleteUser = async (userId) => {
    const res = await fetch(`${API}/api/users/${userId}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete user");
    return res.json();
};

/** Download attendance report as CSV. */
export const downloadAttendanceReport = async (reportDate) => {
    const params = reportDate ? `?report_date=${reportDate}` : "";
    const res = await fetch(`${API}/api/report/download${params}`);
    if (!res.ok) throw new Error("Failed to download report");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `attendance_report_${reportDate || "today"}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
};

/** Send attendance report to an email address. */
export const sendAttendanceReportEmail = async (recipientEmail, reportDate) => {
    const formData = new FormData();
    formData.append("recipient_email", recipientEmail);
    if (reportDate) formData.append("report_date", reportDate);
    const res = await fetch(`${API}/api/report/send-email`, { method: "POST", body: formData });
    return res.json();
};

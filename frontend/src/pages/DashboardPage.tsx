import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function DashboardPage() {
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  const isAdmin = user.role === "admin";
  const isSupport = user.role === "agent" || user.role === "admin";

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {user.full_name}.</p>
      <p>Your role: {user.role}</p>

      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", marginTop: "24px" }}>
        <Link
          to="/tickets"
          style={{
            padding: "16px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            textDecoration: "none",
            minWidth: "180px",
          }}
        >
          View Tickets
        </Link>

        <Link
          to="/tickets/new"
          style={{
            padding: "16px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            textDecoration: "none",
            minWidth: "180px",
          }}
        >
          Create Ticket
        </Link>

        {isAdmin ? (
          <Link
            to="/admin/categories"
            style={{
              padding: "16px",
              border: "1px solid #ddd",
              borderRadius: "8px",
              textDecoration: "none",
              minWidth: "180px",
            }}
          >
            Manage Categories
          </Link>
        ) : null}
      </div>

      {isSupport ? (
        <div style={{ marginTop: "32px" }}>
          <h2>Support View</h2>
          <p>You can review, assign, and progress tickets through the workflow.</p>
        </div>
      ) : (
        <div style={{ marginTop: "32px" }}>
          <h2>Requester View</h2>
          <p>You can create tickets, follow updates, and close or reopen resolved tickets.</p>
        </div>
      )}
    </div>
  );
}
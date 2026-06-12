import { Link } from "react-router-dom";
import { useAuth } from "../../auth/AuthProvider";

export default function NavBar() {
  const { user, logout } = useAuth();

  if (!user) {
    return null;
  }

  const isAdmin = user.role === "admin";

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "16px 24px",
        borderBottom: "1px solid #ddd",
        marginBottom: "24px",
      }}
    >
      <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
        <Link to="/" style={{ fontWeight: "bold", textDecoration: "none" }}>
          Ticket Portal
        </Link>

        <Link to="/tickets" style={{ textDecoration: "none" }}>
          Tickets
        </Link>

        <Link to="/tickets/new" style={{ textDecoration: "none" }}>
          Create Ticket
        </Link>

        {isAdmin ? (
          <Link to="/admin/categories" style={{ textDecoration: "none" }}>
            Categories
          </Link>
        ) : null}
      </div>

      <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
        <span>
          {user.full_name} ({user.role})
        </span>
        <button onClick={logout}>Logout</button>
      </div>
    </nav>
  );
}
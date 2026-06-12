import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getTickets } from "../api/tickets";
import { useAuth } from "../auth/AuthProvider";
import type { TicketRead } from "../types";

export default function TicketListPage() {
  const { user } = useAuth();

  const [tickets, setTickets] = useState<TicketRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

useEffect(() => {
  async function loadTickets() {
    setIsLoading(true);
    setErrorMessage("");

    try {
      const result = await getTickets();
      setTickets(result);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Failed to load tickets");
      }
    } finally {
      setIsLoading(false);
    }
  }

  void loadTickets();
}, []);

  if (!user) {
    return null;
  }

  return (
    <div>
      <h1>Tickets</h1>
      <p>
        {user.role === "employee"
          ? "Showing tickets created by you."
          : "Showing tickets available in the support queue."}
      </p>

      {isLoading ? <p>Loading tickets...</p> : null}

      {!isLoading && errorMessage ? (
        <div style={{ color: "crimson", marginBottom: "16px" }}>{errorMessage}</div>
      ) : null}

      {!isLoading && !errorMessage && tickets.length === 0 ? (
        <p>No tickets found.</p>
      ) : null}

      {!isLoading && !errorMessage && tickets.length > 0 ? (
        <div style={{ display: "grid", gap: "16px", marginTop: "24px" }}>
          {tickets.map((ticket) => (
            <Link
              key={ticket.id}
              to={`/tickets/${ticket.id}`}
              style={{
                display: "block",
                padding: "16px",
                border: "1px solid #ddd",
                borderRadius: "8px",
                textDecoration: "none",
                color: "inherit",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: "16px" }}>
                <strong>{ticket.title}</strong>
                <span>Status: {ticket.status}</span>
              </div>

              <p style={{ marginTop: "8px", marginBottom: "8px" }}>{ticket.description}</p>

              <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", fontSize: "14px" }}>
                <span>Priority: {ticket.priority}</span>
                <span>Category ID: {ticket.category_id}</span>
                <span>
                  Assigned To:{" "}
                  {ticket.assigned_to_user_id ? `User ${ticket.assigned_to_user_id}` : "Unassigned"}
                </span>
              </div>
            </Link>
          ))}
        </div>
      ) : null}
    </div>
  );
}
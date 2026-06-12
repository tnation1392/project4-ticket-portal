import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { createComment, getComments } from "../api/comments";
import { assignTicket, getTicketById, transitionTicket } from "../api/tickets";
import { useAuth } from "../auth/AuthProvider";
import type { CommentRead, TicketRead, TicketStatus } from "../types";

type TransitionAction = {
  label: string;
  toStatus: TicketStatus;
};

function getAvailableTransitions(
  ticket: TicketRead,
  userRole?: string
): TransitionAction[] {
  if (!userRole) {
    return [];
  }

  if (userRole === "employee") {
    if (ticket.status === "resolved") {
      return [
        { label: "Close Ticket", toStatus: "closed" },
        { label: "Reopen Ticket", toStatus: "in_progress" },
      ];
    }

    return [];
  }

  if (userRole === "agent") {
    switch (ticket.status) {
      case "new":
        return [{ label: "Mark Triaged", toStatus: "triaged" }];
      case "triaged":
        return [{ label: "Start Work", toStatus: "in_progress" }];
      case "in_progress":
        return [
          { label: "Waiting for Customer", toStatus: "waiting_for_customer" },
          { label: "Resolve Ticket", toStatus: "resolved" },
        ];
      case "waiting_for_customer":
        return [{ label: "Resume Work", toStatus: "in_progress" }];
      default:
        return [];
    }
  }

  if (userRole === "admin") {
    switch (ticket.status) {
      case "new":
        return [{ label: "Mark Triaged", toStatus: "triaged" }];
      case "triaged":
        return [{ label: "Start Work", toStatus: "in_progress" }];
      case "in_progress":
        return [
          { label: "Waiting for Customer", toStatus: "waiting_for_customer" },
          { label: "Resolve Ticket", toStatus: "resolved" },
        ];
      case "waiting_for_customer":
        return [{ label: "Resume Work", toStatus: "in_progress" }];
      case "resolved":
        return [
          { label: "Close Ticket", toStatus: "closed" },
          { label: "Reopen Ticket", toStatus: "in_progress" },
        ];
      default:
        return [];
    }
  }

  return [];
}

export default function TicketDetailPage() {
  const { ticketId } = useParams();
  const { user } = useAuth();

  const [ticket, setTicket] = useState<TicketRead | null>(null);
  const [isLoadingTicket, setIsLoadingTicket] = useState(true);
  const [ticketErrorMessage, setTicketErrorMessage] = useState("");

  const [comments, setComments] = useState<CommentRead[]>([]);
  const [isLoadingComments, setIsLoadingComments] = useState(true);
  const [commentsErrorMessage, setCommentsErrorMessage] = useState("");

  const [newCommentBody, setNewCommentBody] = useState("");
  const [isInternalComment, setIsInternalComment] = useState(false);
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [commentSubmitError, setCommentSubmitError] = useState("");

  const [isAssigningTicket, setIsAssigningTicket] = useState(false);
  const [assignmentErrorMessage, setAssignmentErrorMessage] = useState("");

  const [isTransitioningTicket, setIsTransitioningTicket] = useState(false);
  const [transitionErrorMessage, setTransitionErrorMessage] = useState("");

  const isSupportUser = user?.role === "agent" || user?.role === "admin";
  const canSelfAssign =
    user?.role === "agent" &&
    !!ticket &&
    ticket.assigned_to_user_id === null;

  const availableTransitions =
    ticket && user ? getAvailableTransitions(ticket, user.role) : [];

  useEffect(() => {
    async function loadTicket() {
      if (!ticketId) {
        setTicketErrorMessage("Missing ticket ID.");
        setIsLoadingTicket(false);
        return;
      }

      setIsLoadingTicket(true);
      setTicketErrorMessage("");

      try {
        const result = await getTicketById(ticketId);
        setTicket(result);
      } catch (error) {
        if (error instanceof Error) {
          setTicketErrorMessage(error.message);
        } else {
          setTicketErrorMessage("Failed to load ticket");
        }
      } finally {
        setIsLoadingTicket(false);
      }
    }

    void loadTicket();
  }, [ticketId]);

  useEffect(() => {
    async function loadComments() {
      if (!ticketId) {
        setCommentsErrorMessage("Missing ticket ID.");
        setIsLoadingComments(false);
        return;
      }

      setIsLoadingComments(true);
      setCommentsErrorMessage("");

      try {
        const result = await getComments(ticketId);
        setComments(result);
      } catch (error) {
        if (error instanceof Error) {
          setCommentsErrorMessage(error.message);
        } else {
          setCommentsErrorMessage("Failed to load comments");
        }
      } finally {
        setIsLoadingComments(false);
      }
    }

    void loadComments();
  }, [ticketId]);

  async function handleCommentSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!ticketId) {
      setCommentSubmitError("Missing ticket ID.");
      return;
    }

    const trimmedBody = newCommentBody.trim();

    if (!trimmedBody) {
      setCommentSubmitError("Comment cannot be empty.");
      return;
    }

    setCommentSubmitError("");
    setIsSubmittingComment(true);

    try {
      const createdComment = await createComment(ticketId, {
        body: trimmedBody,
        is_internal: isSupportUser ? isInternalComment : false,
      });

      setComments((previousComments) => [...previousComments, createdComment]);
      setNewCommentBody("");
      setIsInternalComment(false);
    } catch (error) {
      if (error instanceof Error) {
        setCommentSubmitError(error.message);
      } else {
        setCommentSubmitError("Failed to add comment");
      }
    } finally {
      setIsSubmittingComment(false);
    }
  }

  async function handleAssignToMe() {
    if (!ticketId || !user) {
      setAssignmentErrorMessage("Unable to assign ticket.");
      return;
    }

    setAssignmentErrorMessage("");
    setIsAssigningTicket(true);

    try {
      const updatedTicket = await assignTicket(ticketId, user.id);
      setTicket(updatedTicket);
    } catch (error) {
      if (error instanceof Error) {
        setAssignmentErrorMessage(error.message);
      } else {
        setAssignmentErrorMessage("Failed to assign ticket");
      }
    } finally {
      setIsAssigningTicket(false);
    }
  }

  async function handleTransition(toStatus: TicketStatus) {
    if (!ticketId) {
      setTransitionErrorMessage("Missing ticket ID.");
      return;
    }

    setTransitionErrorMessage("");
    setIsTransitioningTicket(true);

    try {
      const updatedTicket = await transitionTicket(ticketId, toStatus);
      setTicket(updatedTicket);
    } catch (error) {
      if (error instanceof Error) {
        setTransitionErrorMessage(error.message);
      } else {
        setTransitionErrorMessage("Failed to transition ticket");
      }
    } finally {
      setIsTransitioningTicket(false);
    }
  }

  if (isLoadingTicket) {
    return <p>Loading ticket...</p>;
  }

  if (ticketErrorMessage) {
    return (
      <div>
        <p style={{ color: "crimson", marginBottom: "16px" }}>{ticketErrorMessage}</p>
        <Link to="/tickets">Back to Tickets</Link>
      </div>
    );
  }

  if (!ticket) {
    return (
      <div>
        <p>Ticket not found.</p>
        <Link to="/tickets">Back to Tickets</Link>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: "16px" }}>
        <Link to="/tickets">← Back to Tickets</Link>
      </div>

      <h1>{ticket.title}</h1>
      <p>{ticket.description}</p>

      <div
        style={{
          display: "grid",
          gap: "12px",
          marginTop: "24px",
          padding: "16px",
          border: "1px solid #ddd",
          borderRadius: "8px",
          maxWidth: "720px",
        }}
      >
        <div>
          <strong>Status:</strong> {ticket.status}
        </div>

        <div>
          <strong>Priority:</strong> {ticket.priority}
        </div>

        <div>
          <strong>Category ID:</strong> {ticket.category_id}
        </div>

        <div>
          <strong>Created By User ID:</strong> {ticket.created_by_user_id}
        </div>

        <div>
          <strong>Assigned To:</strong>{" "}
          {ticket.assigned_to_user_id ? `User ${ticket.assigned_to_user_id}` : "Unassigned"}
        </div>

        <div>
          <strong>Created At:</strong> {ticket.created_at}
        </div>

        <div>
          <strong>Updated At:</strong> {ticket.updated_at}
        </div>

        <div>
          <strong>Resolved At:</strong> {ticket.resolved_at ?? "Not resolved"}
        </div>

        <div>
          <strong>Closed At:</strong> {ticket.closed_at ?? "Not closed"}
        </div>
      </div>

      <section style={{ marginTop: "24px", maxWidth: "720px" }}>
        <h2>Assignment</h2>

        {assignmentErrorMessage ? (
          <div style={{ color: "crimson", marginBottom: "12px" }}>
            {assignmentErrorMessage}
          </div>
        ) : null}

        {canSelfAssign ? (
          <button
            type="button"
            onClick={handleAssignToMe}
            disabled={isAssigningTicket}
            style={{ padding: "10px 16px" }}
          >
            {isAssigningTicket ? "Assigning..." : "Assign to Me"}
          </button>
        ) : (
          <p>
            {ticket.assigned_to_user_id
              ? `This ticket is assigned to User ${ticket.assigned_to_user_id}.`
              : "This ticket is currently unassigned."}
          </p>
        )}
      </section>

      <section style={{ marginTop: "24px", maxWidth: "720px" }}>
        <h2>Workflow Actions</h2>

        {transitionErrorMessage ? (
          <div style={{ color: "crimson", marginBottom: "12px" }}>
            {transitionErrorMessage}
          </div>
        ) : null}

        {availableTransitions.length === 0 ? (
          <p>No transition actions available.</p>
        ) : (
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            {availableTransitions.map((action) => {
              const requiresAssignment =
                action.toStatus === "in_progress" &&
                ticket.assigned_to_user_id === null;

              return (
                <button
                  key={action.toStatus}
                  type="button"
                  onClick={() => void handleTransition(action.toStatus)}
                  disabled={isTransitioningTicket || requiresAssignment}
                  style={{ padding: "10px 16px" }}
                >
                  {isTransitioningTicket ? "Updating..." : action.label}
                </button>
              );
            })}
          </div>
        )}

        {availableTransitions.some(
          (action) =>
            action.toStatus === "in_progress" &&
            ticket.assigned_to_user_id === null
        ) ? (
          <p style={{ marginTop: "12px", fontSize: "14px", color: "#666" }}>
            Ticket must be assigned before moving to in progress.
          </p>
        ) : null}
      </section>

      <section style={{ marginTop: "32px", maxWidth: "720px" }}>
        <h2>Add Comment</h2>

        <form onSubmit={handleCommentSubmit} style={{ marginBottom: "24px" }}>
          <div style={{ marginBottom: "12px" }}>
            <label htmlFor="commentBody" style={{ display: "block", marginBottom: "8px" }}>
              {isSupportUser ? "Comment" : "Public Comment"}
            </label>
            <textarea
              id="commentBody"
              name="commentBody"
              value={newCommentBody}
              onChange={(event) => setNewCommentBody(event.target.value)}
              rows={4}
              style={{ width: "100%", padding: "8px" }}
            />
          </div>

          {isSupportUser ? (
            <div style={{ marginBottom: "12px" }}>
              <label
                htmlFor="isInternalComment"
                style={{ display: "flex", alignItems: "center", gap: "8px" }}
              >
                <input
                  id="isInternalComment"
                  name="isInternalComment"
                  type="checkbox"
                  checked={isInternalComment}
                  onChange={(event) => setIsInternalComment(event.target.checked)}
                />
                Mark as internal comment
              </label>
            </div>
          ) : null}

          {commentSubmitError ? (
            <div style={{ color: "crimson", marginBottom: "12px" }}>
              {commentSubmitError}
            </div>
          ) : null}

          <button type="submit" disabled={isSubmittingComment} style={{ padding: "10px 16px" }}>
            {isSubmittingComment ? "Adding Comment..." : "Add Comment"}
          </button>
        </form>

        <h2>Comments</h2>

        {isLoadingComments ? <p>Loading comments...</p> : null}

        {!isLoadingComments && commentsErrorMessage ? (
          <div style={{ color: "crimson", marginBottom: "16px" }}>
            {commentsErrorMessage}
          </div>
        ) : null}

        {!isLoadingComments && !commentsErrorMessage && comments.length === 0 ? (
          <p>No comments yet.</p>
        ) : null}

        {!isLoadingComments && !commentsErrorMessage && comments.length > 0 ? (
          <div style={{ display: "grid", gap: "16px", marginTop: "16px" }}>
            {comments.map((comment) => (
              <div
                key={comment.id}
                style={{
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  padding: "16px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: "16px",
                    marginBottom: "8px",
                    fontSize: "14px",
                  }}
                >
                  <span>Author User ID: {comment.author_user_id}</span>
                  <span>{comment.created_at}</span>
                </div>

                <p style={{ marginBottom: "8px" }}>{comment.body}</p>

                {comment.is_internal ? (
                  <span
                    style={{
                      display: "inline-block",
                      padding: "4px 8px",
                      borderRadius: "999px",
                      backgroundColor: "#f3f3f3",
                      fontSize: "12px",
                    }}
                  >
                    Internal Comment
                  </span>
                ) : (
                  <span
                    style={{
                      display: "inline-block",
                      padding: "4px 8px",
                      borderRadius: "999px",
                      backgroundColor: "#eef6ff",
                      fontSize: "12px",
                    }}
                  >
                    Public Comment
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
``

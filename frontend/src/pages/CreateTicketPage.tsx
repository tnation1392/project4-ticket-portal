import {type FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getCategories } from "../api/categories";
import { createTicket } from "../api/tickets";
import type { CategoryRead, TicketPriority } from "../types";

const PRIORITY_OPTIONS: TicketPriority[] = ["low", "medium", "high", "urgent"];

export default function CreateTicketPage() {
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [priority, setPriority] = useState<TicketPriority>("medium");

  const [categories, setCategories] = useState<CategoryRead[]>([]);
  const [isLoadingCategories, setIsLoadingCategories] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function loadCategories() {
      setIsLoadingCategories(true);
      setErrorMessage("");

      try {
        const result = await getCategories();
        setCategories(result);

        if (result.length > 0) {
          setCategoryId(String(result[0].id));
        }
      } catch (error) {
        if (error instanceof Error) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage("Failed to load categories");
        }
      } finally {
        setIsLoadingCategories(false);
      }
    }

    void loadCategories();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");

    const trimmedTitle = title.trim();
    const trimmedDescription = description.trim();

    if (!trimmedTitle || !trimmedDescription || !categoryId) {
      setErrorMessage("Please complete all required fields.");
      return;
    }

    setIsSubmitting(true);

    try {
      const createdTicket = await createTicket({
        title: trimmedTitle,
        description: trimmedDescription,
        category_id: Number(categoryId),
        priority,
      });

      navigate(`/tickets/${createdTicket.id}`);
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Failed to create ticket");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div>
      <h1>Create Ticket</h1>
      <p>Submit a new support request.</p>

      {errorMessage ? (
        <div style={{ color: "crimson", marginBottom: "16px" }}>{errorMessage}</div>
      ) : null}

      {isLoadingCategories ? (
        <p>Loading categories...</p>
      ) : (
        <form onSubmit={handleSubmit} style={{ maxWidth: "640px" }}>
          <div style={{ marginBottom: "16px" }}>
            <label htmlFor="title" style={{ display: "block", marginBottom: "8px" }}>
              Title
            </label>
            <input
              id="title"
              name="title"
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              style={{ width: "100%", padding: "8px" }}
            />
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label htmlFor="description" style={{ display: "block", marginBottom: "8px" }}>
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={6}
              style={{ width: "100%", padding: "8px" }}
            />
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label htmlFor="category" style={{ display: "block", marginBottom: "8px" }}>
              Category
            </label>
            <select
              id="category"
              name="category"
              value={categoryId}
              onChange={(event) => setCategoryId(event.target.value)}
              style={{ width: "100%", padding: "8px" }}
            >
              {categories.map((category) => (
                <option key={category.id} value={String(category.id)}>
                  {category.name}
                </option>
              ))}
            </select>
          </div>

          <div style={{ marginBottom: "16px" }}>
            <label htmlFor="priority" style={{ display: "block", marginBottom: "8px" }}>
              Priority
            </label>
            <select
              id="priority"
              name="priority"
              value={priority}
              onChange={(event) => setPriority(event.target.value as TicketPriority)}
              style={{ width: "100%", padding: "8px" }}
            >
              {PRIORITY_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" disabled={isSubmitting} style={{ padding: "10px 16px" }}>
            {isSubmitting ? "Creating..." : "Create Ticket"}
          </button>
        </form>
      )}
    </div>
  );
}
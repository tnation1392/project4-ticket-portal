import {type FormEvent, useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

export default function LoginPage() {
  const { login, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("employee1@example.com");
  const [password, setPassword] = useState("password123");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setErrorMessage("");
  }, [email, password]);

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage("");
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate("/", { replace: true });
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage("Login failed");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div style={{ maxWidth: "420px", margin: "80px auto", padding: "24px" }}>
      <h1>Ticket Portal Login</h1>
      <p>Sign in to access the ticket portal.</p>

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: "16px" }}>
          <label htmlFor="email" style={{ display: "block", marginBottom: "8px" }}>
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            style={{ width: "100%", padding: "8px" }}
            autoComplete="username"
          />
        </div>

        <div style={{ marginBottom: "16px" }}>
          <label htmlFor="password" style={{ display: "block", marginBottom: "8px" }}>
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            style={{ width: "100%", padding: "8px" }}
            autoComplete="current-password"
          />
        </div>

        {errorMessage ? (
          <div style={{ color: "crimson", marginBottom: "16px" }}>{errorMessage}</div>
        ) : null}

        <button type="submit" disabled={isSubmitting} style={{ padding: "10px 16px" }}>
          {isSubmitting ? "Signing in..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}
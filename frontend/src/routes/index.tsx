import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "../auth/ProtectedRoute";
import AppLayout from "../components/layout/AppLayout";
import LoginPage from "../pages/LoginPage";
import DashboardPage from "../pages/DashboardPage";
import TicketListPage from "../pages/TicketListPage";
import CreateTicketPage from "../pages/CreateTicketPage";
import TicketDetailPage from "../pages/TicketDetailPage";
import CategoryAdminPage from "../pages/CategoryAdminPage";

function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <AppLayout>{children}</AppLayout>
    </ProtectedRoute>
  );
}

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/"
          element={
            <ProtectedLayout>
              <DashboardPage />
            </ProtectedLayout>
          }
        />
        <Route
          path="/tickets"
          element={
            <ProtectedLayout>
              <TicketListPage />
            </ProtectedLayout>
          }
        />
        <Route
          path="/tickets/new"
          element={
            <ProtectedLayout>
              <CreateTicketPage />
            </ProtectedLayout>
          }
        />
        <Route
          path="/tickets/:ticketId"
          element={
            <ProtectedLayout>
              <TicketDetailPage />
            </ProtectedLayout>
          }
        />
        <Route
          path="/admin/categories"
          element={
            <ProtectedLayout>
              <CategoryAdminPage />
            </ProtectedLayout>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

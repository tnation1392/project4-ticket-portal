from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    AGENT = "agent"
    ADMIN = "admin"


class TicketStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


ALLOWED_TICKET_TRANSITIONS = {
    TicketStatus.NEW: {TicketStatus.TRIAGED},
    TicketStatus.TRIAGED: {TicketStatus.IN_PROGRESS},
    TicketStatus.IN_PROGRESS: {
        TicketStatus.WAITING_FOR_CUSTOMER,
        TicketStatus.RESOLVED,
    },
    TicketStatus.WAITING_FOR_CUSTOMER: {TicketStatus.IN_PROGRESS},
    TicketStatus.RESOLVED: {
        TicketStatus.CLOSED,
        TicketStatus.IN_PROGRESS,
    },
    TicketStatus.CLOSED: set(),
}

# Email Reminder System Documentation

## Overview

The BookShare reminder system automatically sends email notifications to borrowers about upcoming due dates and overdue books.

## Architecture

### Components

1. **EmailService** (`app/services/email.py`)
   - Handles email composition and sending via Flask-Mail
   - Templates for different reminder types

2. **ReminderScheduler** (`app/services/scheduler.py`)
   - Business logic for determining which reminders to send
   - Tracks sent notifications in database

3. **APScheduler** (`app/utils/scheduler_config.py`)
   - Automated daily job execution
   - Background scheduler for non-blocking operation

## Reminder Policy

### Timing

Reminders are sent at three key times:

1. **Before Due**: N days before the due date (default: 3 days)
2. **On Due**: On the due date itself
3. **After Due (Overdue)**: N days after the due date (default: 3 days)

**Configuration** (in `.env`):
```bash
REMINDER_BEFORE_DUE=3
REMINDER_AFTER_DUE=3
```

### Scheduling

- **Automated**: Runs daily at 9:00 AM via APScheduler cron job
- **Manual**: Can be triggered via admin dashboard or CLI

## Email Templates

### Before-Due Reminder

```
Subject: Reminder: "Book Title" due soon

Hello [Borrower Name],

This is a friendly reminder that your loan is due soon:

Book: [Title]
Author: [Author]
Due Date: [Date]
Days Remaining: [N]

Please remember to return the book by the due date...
```

### On-Due Reminder

```
Subject: Reminder: "Book Title" due today

Hello [Borrower Name],

This is a reminder that your loan is due TODAY:

Book: [Title]
Author: [Author]
Due Date: [Date]

Please return the book today...
```

### Overdue Reminder

```
Subject: OVERDUE: "Book Title" is overdue

Hello [Borrower Name],

This is an OVERDUE notice for:

Book: [Title]
Author: [Author]
Due Date: [Date]
Days Overdue: [N]

Please return this book as soon as possible...
```

## Notification Tracking

Each sent reminder is recorded in the `notifications` table:

| Field | Description |
|-------|-------------|
| `loan_id` | Foreign key to loan |
| `kind` | Type: `before_due`, `on_due`, `after_due` |
| `scheduled_at` | When reminder should be sent |
| `sent_at` | When reminder was actually sent (NULL if pending) |
| `status` | `pending`, `sent`, or `failed` |

### Deduplication

The system ensures each reminder type is sent only once per loan by checking the notifications table before sending.

## SMTP Configuration

Configure email sending in `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=BookShare Library <noreply@bookshare.local>
SMTP_USE_TLS=True
```

### Gmail Setup

For Gmail:
1. Enable 2-factor authentication
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password in `SMTP_PASSWORD`

### Development Testing

Use **MailHog** for local testing (no real emails sent):

```bash
# Install MailHog
brew install mailhog

# Run MailHog
mailhog

# Update .env
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USE_TLS=False
```

Visit `http://localhost:8025` to see caught emails.

## Usage

### Automatic (Scheduled)

Reminders run automatically every day at 9 AM. No action required.

### Manual Trigger

**Via Admin Dashboard:**
1. Go to `/admin`
2. Click "Send Reminders Now"

**Via CLI:**
```bash
flask send-reminders
```

### Test Email Configuration

```bash
flask test-email
```

## API

### Manual Reminder Trigger

```http
POST /admin/reminders/run
```

**Response (via flash message):**
```
Reminders sent! Before-due: 5, On-due: 2, Overdue: 1, Failed: 0
```

## Workflow

### When a Loan is Created

1. Loan saved to database
2. Three notification records created with `status='pending'`:
   - Before-due (scheduled for due_date - N days)
   - On-due (scheduled for due_date)
   - After-due (scheduled for due_date + N days)

### Daily Processing (9 AM)

1. Scheduler wakes up APScheduler job
2. ReminderScheduler queries all active loans (not returned)
3. For each loan:
   - Check if any reminders are due based on current date
   - Skip if already sent (checked via notifications table)
   - Send email via EmailService
   - Record notification with `status='sent'` and `sent_at=now()`
4. Return statistics

## Performance

### Expected Load

For a library with 1000 active loans:
- Max reminders per day: ~300 (if all loans aligned)
- Typical: ~50-100 reminders/day
- Processing time: <30 seconds

### Optimization

- Batch email sending
- Use email queues for large libraries (not implemented)
- Rate limiting to avoid SMTP throttling

## Error Handling

### Failed Emails

If email sending fails:
- Notification marked as `status='failed'`
- Error logged
- Admin notified via dashboard stats

### Common Issues

**SMTP Authentication Failure:**
- Check username/password
- Verify 2FA and app password for Gmail
- Check SMTP host and port

**Connection Timeout:**
- Verify network connectivity
- Check firewall rules for SMTP port
- Try using `SMTP_PORT=465` with SSL

**Rate Limiting:**
- Gmail: 500 emails/day for free accounts
- Consider using a transactional email service (SendGrid, Mailgun) for production

## CLI Commands

```bash
# Test email configuration
flask test-email

# Send all pending reminders now
flask send-reminders

# Check scheduled jobs (requires app running)
# APScheduler prints job info to logs
```

## Testing

### Unit Tests

Run reminder tests:
```bash
pytest tests/unit/test_reminders.py -v
```

**Coverage:**
- ✓ Email template generation
- ✓ Notification scheduling
- ✓ Overdue detection
- ✓ Deduplication logic
- ✓ Model relationships

### Manual Testing

1. Create a loan with due date = today + 3 days
2. Run `flask send-reminders`
3. Check that before-due reminder sent
4. Verify notification record created in database

## Monitoring

### Check Pending Notifications

```sql
SELECT COUNT(*) FROM notifications WHERE status = 'pending';
```

### Check Failed Notifications

```sql
SELECT * FROM notifications WHERE status = 'failed';
```

### View Recent Activity

```sql
SELECT kind, status, COUNT(*) 
FROM notifications 
WHERE sent_at > datetime('now', '-1 day')
GROUP BY kind, status;
```

## Future Enhancements

1. **HTML Email Templates**: Rich formatting with CSS
2. **Email Preferences**: Let borrowers opt-out or customize frequency
3. **SMS Notifications**: Alternative to email
4. **Digest Emails**: Single email with all borrower's loans
5. **Admin Notifications**: Daily summary for librarians
6. **Email Queue**: Redis-based queue for high-volume libraries
7. **Analytics**: Track open rates and engagement

## Security Considerations

- Store SMTP credentials in environment variables, never in code
- Use TLS/SSL for email transmission
- Validate email addresses before sending
- Rate limit manual triggers to prevent abuse
- Log all email activity for audit trail

---

**For more information**, see:
- `app/services/email.py` - Email sending logic
- `app/services/scheduler.py` - Reminder scheduling
- `app/utils/scheduler_config.py` - APScheduler config
- `tests/unit/test_reminders.py` - Unit tests

{% extends 'base.html' %}

{% block title %}Student Payments{% endblock %}

{% block content %}
<section class="panel">
  <h2>Payment History</h2>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Amount</th>
          <th>Due Date</th>
          <th>Paid Date</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {% for payment in payments %}
        <tr>
          <td>₹{{ payment.amount }}</td>
          <td>{{ payment.due_date }}</td>
          <td>{{ payment.paid_date or '-' }}</td>
          <td>{{ payment.status }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</section>
{% endblock %}

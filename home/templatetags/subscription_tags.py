from django import template

from home.models import Member

register = template.Library()


@register.filter(name='member_month')
def member_month(member, month):
    return {
        "month": month,
        "member": member,
    }


@register.filter
def get_subscriptions(member: Member, subscriptions):
    """Concatenates the value with the argument."""
    return subscriptions.filter(member=member)


@register.filter()
def get_subscription(data, subscriptions):
    """Concatenates the value with the argument."""
    return subscriptions.filter(member=data.get("member"), subscription_month=data.get("month")).first()

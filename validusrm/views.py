from datetime import datetime
from django.views.generic import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Investment, Commitment

#TODO Add validation of input data from form.
#TODO Consider using Django Forms with appropriate 'clean' functionality


class InvestmentMixin(object):
    def retrieve_investment(self, investment_name):
        investment_found = False
        investment = Investment.objects.none()
        try:
            investment = Investment.objects.get(name=investment_name)
            investment_found = True
        except:
            pass

        return investment_found, investment


class Withdraw(View, InvestmentMixin):
    """Withdraw an amount from an investment fund by date order FIFO"""
    def post(self, request):
        investment_name = request.POST.get('investment_name', '')
        self.amount = float(request.POST.get('amount', '0.0'))

        investment_found, investment = self.retrieve_investment(investment_name)

        state = self.withdraw_funds(investment)

        if not investment_found:
            return HttpResponse("Investment not found: no funds", status=402)
        elif not state:
            return HttpResponse("Insufficient funds available", status=402)
        else:
            return redirect('/investments')

    def check_funds_are_available(self, investments):
        running_total_test = 0.0
        for c in investments:
            running_total_test += c.amount
        if self.amount > running_total_test:
            return False
        else:
            return True

    def withdraw_funds(self, i):
        investments = i.commitments.all().order_by('date', 'date')
        withdrawal = 0.0
        running_total = 0.0
        if not self.check_funds_are_available(investments):
            return False

        for c in investments:
            if (self.amount - running_total) > c.amount:
                withdrawal += c.amount
                running_total += withdrawal
                c.amount = 0
                c.save()
            elif (self.amount - running_total) > 0.0:
                withdrawal = self.amount - withdrawal
                running_total = withdrawal
                c.amount = c.amount - withdrawal
                c.save()
                break

        return True

class Deposit(View, InvestmentMixin):
    """Deposit new funds for a commitment in as an Investment by name"""
    def post(self, request):
        investment_name = request.POST.get('investment_name', '')
        self.commitment_id = request.POST.get('commitment_id', '')
        self.fund_id = request.POST.get('fund_id', '')
        self.the_date = request.POST.get('date', datetime.now())
        self.amount = float(request.POST.get('amount', '0.0'))

        investment_found, investment = self.retrieve_investment(investment_name)

        new_investment = True
        if investment:
            new_investment = False
            self.handle_commitment(investment, False)
        if new_investment:
            i = Investment()
            i.name = investment_name
            self.handle_commitment(i)
        return redirect('/investments')

    def handle_commitment(self, i, save=True):
        c = Commitment()
        c.identifier = self.commitment_id
        c.fund = self.fund_id
        c.date = datetime.strptime(self.the_date, '%Y-%m-%d').date()
        c.amount = self.amount
        c.save()
        if save:
            i.save()
        i.commitments.add(c)


class Investments(View):
    """Display results and allow for deposits and withdrawals"""
    def get(self, request):
        investments = Investment.objects.all().prefetch_related('commitments')
        context = {
            'investments': investments,
        }

        return render(request, 'investments.html', context)
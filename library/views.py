from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.template.context_processors import request
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from authentication.models import UserAccount
from .models import Book, Borrow, Review, Category
from .forms import DepositForm, ReviewForm

########## Home Page View ##########
class HomepageView(View):
    def get(self, request, category_slug = None):
        data = Book.objects.all()
        categories = Category.objects.all()
        if category_slug is not None:
            category = Category.objects.get(category = category_slug)
            data = Book.objects.filter(book_category = category)
            return render(request, 'library/homepage.html', {'data': data, 'categories': categories})
        return render(request, 'library/homepage.html', {'data': data, 'categories': categories})


########## Book Detail View ##########
class BookDetailView(DetailView):
    model = Book
    pk_url_kwarg = 'id'
    template_name = 'library/book_detail.html'

    def post(self, request, id, *args, **kwargs):
        book = self.get_object()
        review_form = ReviewForm(data=request.POST)

        # Borrowed user can only write review
        borrowed = Borrow.objects.filter(username=request.user.username, book_id=book.id).exists()
        if borrowed:
            if review_form.is_valid():
                new_review = review_form.save(commit=False)
                new_review.book = book
                new_review.user = request.user
                new_review.save()
                messages.success(request, "Review Posted Successfully!")
                return redirect('library:book_detail', id=book.id)
        else:
            messages.warning(request, "You can only review books that you have borrowed!")
            return redirect('library:book_detail', id=book.id)
        context = self.get_context_data(review_form=review_form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review_form = kwargs.get('review_form', ReviewForm())

        context['review_form'] = review_form
        context['reviews'] = self.object.reviews.all()
        return context


########## User Profile View ##########
class UserProfileView(LoginRequiredMixin, View):
    template_name = 'library/user_profile.html'

    def get(self, request, *args, **kwargs):
        user_account = UserAccount.objects.get(user=request.user)

        user_borrows = Borrow.objects.filter(username=request.user.username)

        borrow_records = []
        for borrow in user_borrows:
            book = Book.objects.get(id=borrow.book_id)
            borrow_records.append({
                'borrow_id': borrow.id,
                'book_title': book.book_title,
                'book_borrowing_price': book.book_borrowing_price,
                'borrowing_on': borrow.borrowing_on
            })

        context = {
            'user': request.user,
            'balance': user_account.balance,
            'borrow_records': borrow_records
        }

        return render(request, self.template_name, context)


########## Money Deposit View ##########
class DepositMoneyView(View):
    model = UserAccount
    form_class = DepositForm
    template_name = 'library/deposit_money.html'
    success_url = '/user_profile/'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['balance']
            user_account = self.model.objects.get(user=request.user)
            user_account.balance += amount
            user_account.save()
            messages.success(request, f'Successfully deposited {amount}')

            # Email Send
            mail_subject = 'Money Deposit Successful!'
            message = render_to_string('library/email/deposit.html', {
                'user' : request.user,
                'amount' : amount,
                'balance' : user_account.balance
            })
            sent_email = request.user.email
            send_mess = EmailMultiAlternatives(mail_subject, '', to=[sent_email])
            send_mess.attach_alternative(message, 'text/html')
            send_mess.send()

            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


########## Borrowing Book View ##########
class BorrowingView(View):
    model = Borrow
    success_url = '/user_profile/'

    def get(self, request, *args, **kwargs):
        return redirect('library:homepage')

    def post(self, request, id, *args, **kwargs):
        # book_id = request.POST.get('book_id')
        print(id)
        book_id = id
        if book_id:
            book = Book.objects.get(id=book_id)
            user_account = UserAccount.objects.get(user=request.user)
            if user_account.balance >= book.book_borrowing_price:
                user_account.balance -= book.book_borrowing_price
                user_account.save()
                print('Borrowed')
                Borrow.objects.create(book_id=book.id, username=request.user.username)
                messages.success(request, 'Book borrowed successfully')

                # Email Send
                mail_subject = 'Book Borrowing Successful!'
                message = render_to_string('library/email/borrow.html', {
                    'user': request.user,
                    'book': book,
                    'balance': user_account.balance
                })
                sent_email = request.user.email
                send_mess = EmailMultiAlternatives(mail_subject, '', to=[sent_email])
                send_mess.attach_alternative(message, 'text/html')
                send_mess.send()

                return redirect(self.success_url)
            else:
                messages.warning(request, 'Insufficient balance to borrow this book')
                return redirect('library:book_detail', id=book_id)

        messages.error(request, 'Failed to borrow book')
        return redirect('library:homepage')
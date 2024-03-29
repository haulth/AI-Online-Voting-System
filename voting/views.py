import base64
import os
from django.shortcuts import render, redirect, reverse
from account.views import account_login
from .models import Position, Candidate, Voter, Votes
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.text import slugify
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
# Create your views here.
from datetime import datetime
from django.shortcuts import render



#Các thư viện cần thiết



def index(request):
    if not request.user.is_authenticated:
        return account_login(request)
    context = {}
    # return render(request, "voting/login.html", context)

def generate_ballot(display_controls=False):
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1
    instruction = ""
    # return None
    hide = 0
    for position in positions:
        if position.max_vote < 1:
            hide += 1
        else:
            name = position.name
            position_name = slugify(name)
            candidates = Candidate.objects.filter(position=position)
            for candidate in candidates:
                if position.max_vote > 1:
                    instruction = "Bạn có thể chọn tối đa " + \
                        str(position.max_vote) + " đại biểu"
                    input_box = '<input type="checkbox" value="'+str(candidate.id)+'" class="flat-red ' + \
                        position_name+'" name="' + \
                        position_name+"[]" + '">'

                else:
                    instruction = "Chỉ chọn một đại biểu "
                    input_box = '<input value="'+str(candidate.id)+'" type="radio" class="flat-red ' + \
                        position_name+'" name="'+position_name+'">'
                image = "/media/" + str(candidate.photo)
                candidates_data = candidates_data + '<li>' + input_box + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="'+candidate.fullname+'" data-bio="'+candidate.bio+'"><i class="fa fa-search"></i> Chi tiết</button><img src="' + \
                    image+'" height="100px" width="100px" class="clist"><span class="cname clist">' + \
                    candidate.fullname+'</span></li>'
            up = ''
            if position.priority == 1:
                up = 'disabled'
            down = ''

            if position.priority == (positions.count()-hide):
                down = 'disabled'
            output = output + f"""<div class="row">	<div class="col-xs-12"><div class="box box-solid" id="{position.id}">
                <div class="box-header with-border">
                <h3 class="box-title"><b>{name}</b></h3>"""

            if display_controls:
                output = output + f""" <div class="pull-right box-tools">
            <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
            <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
            </div>"""

            output = output + f"""</div>
            <div class="box-body">
            <p>{instruction}
            <span class="pull-right">
            <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Làm mới</button>
            </span>
            </p>
            <div id="candidate_list">
            <ul>
            {candidates_data}
            </ul>
            </div>
            </div>
            </div>
            </div>
            </div>
            """
            position.priority = num
            position.save()
            num = num + 1
            candidates_data = ''
        if positions.count() == hide:
            output = '<div class="text-center"><div class="col-xs-12"><div class="box box-solid"><div class="box-header with-border"><h3 class="box-title"><b>Tạm thời chưa có bình chọn nào!</b></h3></div><div class="box-body"><p>Vui lòng đợi trong giây lát!</p></div> <div ><button type="button" id="refresh" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Làm mới</button></div></div></div></div>'
            break
    return output


def generate_ballot_for_admin(display_controls=True):
    positions = Position.objects.order_by('priority').all()
    output = ""
    candidates_data = ""
    num = 1
    # return None
    hide = 0
    for position in positions:

        name = position.name
        position_name = slugify(name)
        candidates = Candidate.objects.filter(position=position)
        for candidate in candidates:

            if position.max_vote > 1:
                instruction = "Bạn có thể chọn tối đa " + \
                    str(position.max_vote) + " đại biểu"
                input_box = '<input type="checkbox" value="'+str(candidate.id)+'" class="flat-red ' + \
                    position_name+'" name="' + \
                    position_name+"[]" + '">'

            else:
                if position.max_vote < 1:
                    instruction = "Bình chọn này không được hiển thị"
                else:
                    instruction = "Chỉ chọn một đại biểu"
                input_box = '<input value="'+str(candidate.id)+'" type="radio" class="flat-red ' + \
                    position_name+'" name="'+position_name+'">'
            image = "/media/" + str(candidate.photo)
            candidates_data = candidates_data + '<li>' + input_box + '<button type="button" class="btn btn-primary btn-sm btn-flat clist platform" data-fullname="'+candidate.fullname+'" data-bio="'+candidate.bio+'"><i class="fa fa-search"></i> Chi tiết</button><img src="' + \
                image+'" height="100px" width="100px" class="clist"><span class="cname clist">' + \
                candidate.fullname+'</span></li>'
        up = ''
        if position.priority == 1:
            up = 'disabled'
        down = ''

        if position.priority == (positions.count()-hide):
            down = 'disabled'
        output = output + f"""<div class="row">	<div class="col-xs-12"><div class="box box-solid" id="{position.id}">
             <div class="box-header with-border">
            <h3 class="box-title"><b>{name}</b></h3>"""

        if display_controls:
            output = output + f""" <div class="pull-right box-tools">
        <button type="button" class="btn btn-default btn-sm moveup" data-id="{position.id}" {up}><i class="fa fa-arrow-up"></i> </button>
        <button type="button" class="btn btn-default btn-sm movedown" data-id="{position.id}" {down}><i class="fa fa-arrow-down"></i></button>
        </div>"""

        output = output + f"""</div>
        <div class="box-body">
        <p>{instruction}
        <span class="pull-right">
        <button type="button" class="btn btn-success btn-sm btn-flat reset" data-desc="{position_name}"><i class="fa fa-refresh"></i> Reset</button>
        </span>
        </p>
        <div id="candidate_list">
        <ul>
        {candidates_data}
        </ul>
        </div>
        </div>
        </div>
        </div>
        </div>
        """
        position.priority = num
        position.save()
        num = num + 1
        candidates_data = ''
    return output


def fetch_ballot(request):
    output = generate_ballot_for_admin(display_controls=True)
    return JsonResponse(output, safe=False)


def generate_otp():
    """Link to this function
    https://www.codespeedy.com/otp-generation-using-random-module-in-python/
    """
    import random as r
    otp = ""
    for i in range(r.randint(5, 8)):
        otp += str(r.randint(1, 9))
    return otp


def dashboard(request):
    positions = Position.objects.all().order_by('priority')
    candidates = Candidate.objects.all()
    voters = Voter.objects.all()
    voted_voters = Voter.objects.filter(voted=1)
    chart_data = {}

    for position in positions:
        if position.max_vote < 1:
            continue
            
        total_votes = Votes.objects.filter(candidate__position=position).count()
        candidates_data = []
        for candidate in Candidate.objects.filter(position=position):
            votes = Votes.objects.filter(candidate=candidate).count()
            percent = (votes / total_votes) * 100 if total_votes > 0 else 0
            candidates_data.append({'name': candidate.fullname, 'votes': votes, 'percent': percent})

        chart_data[position] = {'candidates': candidates_data, 'pos_id': position.id}
    try:
        with open('./vote_time_start.txt', 'r') as f:
            vote_time_str_start = f.read().strip()
        # Chuyển đổi thời gian kết thúc bình chọn từ định dạng string sang datetime object
        vote_time_start = datetime.fromisoformat(vote_time_str_start)
        with open('./vote_time_end.txt', 'r') as f:
            vote_time_str_end = f.read().strip()
        # Chuyển đổi thời gian kết thúc bình chọn từ định dạng string sang datetime object
        vote_time_end = datetime.fromisoformat(vote_time_str_end)

        # Tính thời gian còn lại đến khi kết thúc bình chọn
        if vote_time_start > datetime.now():
        
            time_left_str = "-1"
            messages.error(request, "Bình chọn chưa bắt đầu")
            
        # Nếu thời gian bình chọn đã bắt đầu
        elif vote_time_start < datetime.now() < vote_time_end:
 
            time_left = vote_time_end - datetime.now()
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Trả về thời gian còn lại dưới dạng chuỗi "giờ:phút:giây"
            time_left_str = f"{int(time_left.days * 24 + hours)}:{minutes:02d}:{seconds:02d}"
        elif vote_time_end < datetime.now():
       
            time_left_str = "00:00:00"
            messages.error(request, "Bình chọn đã kết thúc")
            
        else:

            time_left_str = "-1"
            messages.error(request, "Bình chọn chưa bắt đầu")
            
    except Exception as e:
        print (e)
        time_left_str = "-1"
        messages.error(request, "Bình chọn chưa bắt đầu")
        

    user = request.user
    # * Check if this voter has been verified
    if user.voter.otp is None or user.voter.verified == False:
        if not settings.SEND_OTP:
            # Bypass
            msg = bypass_otp()
            messages.success(request, msg)
            return redirect(reverse('show_ballot'))
        else:
            return redirect(reverse('voterVerify'))
    else:
        if user.voter.voted:  # * User has voted
            # To display election result or candidates I voted for ?
            context = {
                'my_votes': Votes.objects.filter(voter=user.voter),
                'position_count': positions.count(),
                'candidate_count': candidates.count(),
                'voters_count': voters.count(),
                'voted_voters_count': voted_voters.count(),
                'chart_data': chart_data,
                'time_left_str': time_left_str,
                
            }
            return render(request, "voting/voter/result.html", context)
        else:
            return redirect(reverse('show_ballot'))


def verify(request):
    context = {
        'page_title': 'Xác minh OTP'
    }
    return render(request, "voting/voter/verify.html", context)


def resend_otp(request):
    """API For SMS
    I used https://www.multitexter.com/ API to send SMS
    You might not want to use this or this service might not be available in your Country
    For quick and easy access, Toggle the SEND_OTP from True to False in settings.py
    """
    user = request.user
    voter = user.voter
    error = False
    if settings.SEND_OTP:
        if voter.otp_sent >= 3:
            error = True
            response = "Bạn đã yêu cầu OTP ba lần. Bạn không thể làm điều này một lần nữa! Vui lòng nhập OTP đã gửi trước đó"
        else:
            phone = voter.phone
            # Now, check if an OTP has been generated previously for this voter
            otp = voter.otp
            if otp is None:
                # Generate new OTP
                otp = generate_otp()
                voter.otp = otp
                voter.save()
            try:
                msg = "Dear " + str(user) + ", kindly use " + \
                    str(otp) + " as your OTP"
                message_is_sent = send_sms(phone, msg)
                if message_is_sent:  # * OTP was sent successfully
                    # Update how many OTP has been sent to this voter
                    # Limited to Three so voters don't exhaust OTP balance
                    voter.otp_sent = voter.otp_sent + 1
                    voter.save()

                    response = "OTP đã được gửi đến số điện thoại của bạn. Vui lòng cung cấp nó trong hộp được cung cấp bên dưới"
                else:
                    error = True
                    response = "OTP không được gửi. Vui lòng thử lại"
            except Exception as e:
                response = "Không thể gửi OTP." + str(e)

                # * Send OTP
    else:
        #! Update all Voters record and set OTP to 0000
        #! Bypass OTP verification by updating verified to 1
        #! Redirect voters to ballot page
        response = bypass_otp()
    return JsonResponse({"data": response, "error": error})


def bypass_otp():
    Voter.objects.all().filter(otp=None, verified=False).update(otp="0000", verified=True)
    response = "Vui lòng bỏ phiếu bầu của bạn"
    return response


def send_sms(phone_number, msg):
    """Read More
    https://www.multitexter.com/developers
    """
    import requests
    import os
    import json
    response = ""
    email = os.environ.get('SMS_EMAIL')
    password = os.environ.get('SMS_PASSWORD')
    if email is None or password is None:
        raise Exception("Email/Password cannot be Null")
    url = "https://app.multitexter.com/v2/app/sms"
    data = {"email": email, "password": password, "message": msg,
            "sender_name": "OTP", "recipients": phone_number, "forcednd": 1}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    response = r.json()
    status = response.get('status', 0)
    if str(status) == '1':
        return True
    else:
        return False


def verify_otp(request):
    error = True
    if request.method != 'POST':
        messages.error(request, "Truy cập bị từ chối")
    else:
        otp = request.POST.get('otp')
        if otp is None:
            messages.error(request, "Vui lòng cung cấp OTP hợp lệ")
        else:
            # Get User OTP
            voter = request.user.voter
            db_otp = voter.otp
            if db_otp != otp:
                messages.error(request, "OTP đã cung cấp không hợp lệ")
            else:
                messages.success(
                    request, "Bây giờ bạn đã được xác minh. Hãy bỏ phiếu của bạn")
                voter.verified = True
                voter.save()
                error = False
    if error:
        return redirect(reverse('voterVerify'))
    return redirect(reverse('show_ballot'))

# show form bình chọn và hiển thị thời gian

def show_ballot(request):
    try:
        with open('./vote_time_start.txt', 'r') as f:
            vote_time_str_start = f.read().strip()
        # Chuyển đổi thời gian kết thúc bình chọn từ định dạng string sang datetime object
        vote_time_start = datetime.fromisoformat(vote_time_str_start)
        with open('./vote_time_end.txt', 'r') as f:
            vote_time_str_end = f.read().strip()
        # Chuyển đổi thời gian kết thúc bình chọn từ định dạng string sang datetime object
        vote_time_end = datetime.fromisoformat(vote_time_str_end)

        # Tính thời gian còn lại đến khi kết thúc bình chọn

        if vote_time_start > datetime.now():
     
            time_left_str = "-1"
            messages.error(request, "Bình chọn chưa bắt đầu")
            
        # Nếu thời gian bình chọn đã bắt đầu
        elif vote_time_start < datetime.now() < vote_time_end:
    
            time_left = vote_time_end - datetime.now()
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Trả về thời gian còn lại dưới dạng chuỗi "giờ:phút:giây"
            time_left_str = f"{int(time_left.days * 24 + hours)}:{minutes:02d}:{seconds:02d}"
        elif vote_time_end < datetime.now():
          
            time_left_str = "00:00:00"
            messages.error(request, "Bình chọn đã kết thúc")
            
        else:
  
            time_left_str = "-1"
            messages.error(request, "Bình chọn chưa bắt đầu")
            
    except Exception as e:
        print(e)
        messages.error(request, "Bình chọn đến thời hạn")
        
    # Tính toán số giờ, phút và giây từ đối tượng timedelta

    # # Trả về time_left để hiển thị countdown trên giao diện
    if request.user.voter.voted:
        messages.error(request, "Bạn đã bình chọn rồi")
        return redirect(reverse('voterDashboard'))
    ballot = generate_ballot(display_controls=False)
    return render(request, "voting/voter/ballot.html", {'ballot': ballot, 'time_left_str': time_left_str,'page_title': 'Bỏ phiếu'})


def preview_vote(request):
    pass
    if request.method != 'POST':
        error = True
        response = "Vui lòng duyệt hệ thống đúng cách"
    else:
        output = ""
        form = dict(request.POST)
        # We don't need to loop over CSRF token
        form.pop('csrfmiddlewaretoken', None)
        error = False
        data = []
        positions = Position.objects.all()
        for position in positions:
            max_vote = position.max_vote
            pos = slugify(position.name)
            pos_id = position.id
            if position.max_vote > 1:
                this_key = pos + "[]"
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                if len(form_position) > max_vote:
                    error = True
                    response = "Bạn chỉ có thể chọn " + \
                        str(max_vote) + " đại biểu cho " + position.name
                else:
                    # for key, value in form.items():
                    start_tag = f"""
                       <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'>
                                <ul style='list-style-type:none; margin-left:-40px'>
                                
                    
                    """
                    end_tag = "</ul></span></div><hr/>"
                    data = ""
                    for form_candidate_id in form_position:
                        try:
                            candidate = Candidate.objects.get(
                                id=form_candidate_id, position=position)
                            data += f"""
		                      	<li><i class="fa fa-check-square-o"></i> {candidate.fullname}</li>
                            """
                        except:
                            error = True
                            response = "Xin vui lòng, duyệt hệ thống đúng cách"
                    output += start_tag + data + end_tag
            elif position.max_vote < 1:
                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position)
                    output += f"""
                            <div class='row votelist' style='padding-bottom: 2px'>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
		                    </div>
                      <hr/>
                    """
                except Exception as e:
                    error = True
                    response = "Xin vui lòng, duyệt hệ thống đúng cách"
            else:
                this_key = pos
                form_position = form.get(this_key)
                if form_position is None:
                    continue
                # Max Vote == 1

                try:
                    form_position = form_position[0]
                    candidate = Candidate.objects.get(
                        position=position, id=form_position)
                    output += f"""
                            <div class='row votelist' style='padding-bottom: 2px'>
                                
                                <h3>Bình chọn này đang ẩn</h3>
		                      	<span class='col-sm-4'><span class='pull-right'><b>{position.name} :</b></span></span>
		                      	<span class='col-sm-8'><i class="fa fa-check-circle-o"></i> {candidate.fullname}</span>
		                    </div>
                      <hr/>
                    """
                except Exception as e:
                    error = True
                    response = "Xin vui lòng, duyệt hệ thống đúng cách"
    context = {
        'error': error,
        'list': output
    }
    return JsonResponse(context, safe=False)


def submit_ballot(request):
    if request.method != 'POST':
        messages.error(request, "Xin vui lòng, duyệt hệ thống đúng cách")
        return redirect(reverse('show_ballot'))

    # Verify if the voter has voted or not
    voter = request.user.voter
    if voter.voted:
        messages.error(request, "Bạn đã bình chọn rồi")
        return redirect(reverse('voterDashboard'))

    form = dict(request.POST)
    form.pop('csrfmiddlewaretoken', None)  # Pop CSRF Token
    form.pop('submit_vote', None)  # Pop Submit Button

    # Ensure at least one vote is selected
    if len(form.keys()) < 1:
        messages.error(request, "Vui lòng chọn ít nhất một ứng viên")
        return redirect(reverse('show_ballot'))
    positions = Position.objects.all()
    form_count = 0
    for position in positions:
        max_vote = position.max_vote
        pos = slugify(position.name)
        pos_id = position.id
        if position.max_vote > 1:
            this_key = pos + "[]"
            form_position = form.get(this_key)
            if form_position is None:
                continue
            if len(form_position) > max_vote:
                messages.error(request, "Bạn chỉ có thể chọn " +
                               str(max_vote) + " đại biểu cho " + position.name)
                return redirect(reverse('show_ballot'))
            else:
                for form_candidate_id in form_position:
                    form_count += 1
                    try:
                        candidate = Candidate.objects.get(
                            id=form_candidate_id, position=position)
                        vote = Votes()
                        vote.candidate = candidate
                        vote.voter = voter
                        vote.position = position
                        vote.save()
                    except Exception as e:
                        messages.error(
                            request, "Xin vui lòng, duyệt hệ thống đúng cách " + str(e))
                        return redirect(reverse('show_ballot'))
        else:
            this_key = pos
            form_position = form.get(this_key)
            if form_position is None:
                continue
            # Max Vote == 1
            form_count += 1
            try:
                form_position = form_position[0]
                candidate = Candidate.objects.get(
                    position=position, id=form_position)
                vote = Votes()
                vote.candidate = candidate
                vote.voter = voter
                vote.position = position
                vote.save()
            except Exception as e:
                messages.error(
                    request, "Xin vui lòng, duyệt hệ thống đúng cách " + str(e))
                return redirect(reverse('show_ballot'))
    # Count total number of records inserted
    # Check it viz-a-viz form_count
    inserted_votes = Votes.objects.filter(voter=voter)
    if (inserted_votes.count() != form_count):
        # Delete
        inserted_votes.delete()
        messages.error(request, "Vui lòng thử bỏ phiếu lại!")
        return redirect(reverse('show_ballot'))
    else:
        # Update Voter profile to voted
        voter.voted = True
        voter.save()
        messages.success(request, "Cảm ơn đã bỏ phiếu")
        return redirect(reverse('voterDashboard'))

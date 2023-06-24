from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="adminDashboard"),
    # * Voters
    path('voters', views.voters, name="adminViewVoters"),
    path('voters/view', views.view_voter_by_id, name="viewVoter"),
    path('voters/delete', views.deleteVoter, name='deleteVoter'),
    path('voters/QRVoter', views.QRVoter, name='QRVoter'),
    path('voters/delete_all', views.deleteAllVoters, name='deleteAllVoters'),
    path('voters/update', views.updateVoter, name="updateVoter"),
    path('delete-all/', views.deleteAllVoters, name='deleteAllVoters'),
    path('update-acc/', views.updateAcc, name='updateAcc'),
    path('get_vote_progress/', views.get_vote_progress, name='get_vote_progress'),
    path('voters_result/', views.voter_result, name='voters_result'),

    # * Position
    path('position/view', views.view_position_by_id, name="viewPosition"),
    path('position/update', views.updatePosition, name="updatePosition"),
    path('position/delete', views.deletePosition, name='deletePosition'),
    path('positions/view', views.viewPositions, name='viewPositions'),

    # * Candidate
    path('candidate/', views.viewCandidates, name='viewCandidates'),
    path('candidate/update', views.updateCandidate, name="updateCandidate"),
    path('candidate/delete', views.deleteCandidate, name='deleteCandidate'),
    path('candidate/view', views.view_candidate_by_id, name='viewCandidate'),

    # * Settings (Ballot Position and Election Title)
    path("settings/ballot/position", views.ballot_position, name='ballot_position'),
    path("settings/ballot/title/", views.ballot_title, name='ballot_title'),
    path("settings/ballot/position/update/<int:position_id>/<str:up_or_down>/",
         views.update_ballot_position, name='update_ballot_position'),

    # * Votes
    path('votes/view', views.viewVotes, name='viewVotes'),
    path('votes/reset/', views.resetVote, name='resetVote'),
    path('votes/print/', views.PrintView.as_view(), name='printResult'),
    path('save-vote-time/', views.save_vote_time, name='save_vote_time'),
    path('delete_vote_time/', views.delete_vote_time, name='delete_vote_time'),
    path('infovoter/', views.infoVoter, name="infoVoter"),
    
    #face recognition
    path('interface/', views.interface, name='interface'),
    path('identified/', views.identified, name='identified'),
    path('attendee_list/', views.attendee_list, name='attendee_list'),
    path('face_detection/', views.face_detection, name='face_detection'),
    path('ad_train/', views.ad_train, name='ad_train'),
    path('train/', views.train, name='train'),
    path('timetrain/', views.timetrain, name='timetrain'),
    path('list_attendance/', views.list_attendance, name='list_attendance'),
    path('upload_images/', views.upload_images, name="upload_images"),
    path('create_folder/', views.create_folder, name='create_folder'),
    path('register/', views.account_register, name="account_register"),
]

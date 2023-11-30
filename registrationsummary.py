from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask, render_template, send_file, Response, make_response
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import tempfile
import os
from flask_ckeditor import CKEditor
from datetime import datetime
from barcode import Code128
from barcode.writer import ImageWriter
from xhtml2pdf import pisa
import io

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345'  # Replace with a secure random key
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uhid = db.Column(db.String(50))
    title = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    patient_name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email_id = db.Column(db.String(100))
    contact_number = db.Column(db.String(15))
    Address = db.Column(db.String(10))
    current_date = datetime.now().date()

class Testmaster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    testcode = db.Column(db.String(50))
    testname = db.Column(db.String(100))
    specimentype = db.Column(db.String(50))    
    current_date = datetime.now().date()
    
class refdr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    DoctorCode = db.Column(db.String(50))
    DoctorName = db.Column(db.String(100))
    Qualification = db.Column(db.String(50))    
    Specialisation =db.Column(db.String(50))  
    Address =db.Column(db.String(50))
    Mobile =db.Column(db.String(50))     
    current_date = datetime.now().date()
    
class pathologist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    DoctorCode = db.Column(db.String(50))
    DoctorName = db.Column(db.String(100))
    Qualification = db.Column(db.String(50))    
    Specialisation =db.Column(db.String(50))  
    Address =db.Column(db.String(50))
    Mobile =db.Column(db.String(50))  
    signature = db.Column(db.String(50))
    current_date = datetime.now().date()
    
class reportformat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.String(50))
    reportname = db.Column(db.String(100))
    template = db.Column(db.String(50))    
    current_date = datetime.now().date()   

class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uhid = db.Column(db.String(50))
    title = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    patient_name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    age = db.Column(db.Integer)
    email_id = db.Column(db.String(100))
    contact_number = db.Column(db.String(15))
    Address = db.Column(db.String(10))
    current_date = datetime.now().date()  
    ref_dr =  db.Column(db.String(10))
    select_test = db.Column(db.String(10))
    visitid = db.Column(db.String(10))
    
class generatereport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pathologistid = db.Column(db.String(50))
    patientname = db.Column(db.String(10))
    templateid = db.Column(db.String(10))  
    template =    db.Column(db.String(10))
    current_date = datetime.now().date()
    visitid=db.Column(db.String(10))  

class router(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aetitle = db.Column(db.String(50))
    ipaddress = db.Column(db.String(10))
    portnumber = db.Column(db.String(10))  

    
@app.route('/register', methods=['GET', 'POST'])
def index():
    lastuhid_code=''
    patientmaster = Patient.query.order_by(Patient.id.desc()).first()
    if patientmaster and patientmaster.uhid:
        uhid_code = int(patientmaster.uhid[1:])
        lastuhid_code = f'U{uhid_code + 1:05}'
    else:
        lastuhid_code = 'U00001'
    if request.method == 'POST':
        title = request.form.get('title')
        gender = request.form.get('gender')
        patient_name= request.form.get('patient_name')
        dob= request.form.get('dob')
        age= request.form.get('age')
        email_id= request.form.get('email_id')
        contact_number= request.form.get('contact_number')
        Address= request.form.get('Address')
        

        
        patient = Patient(
            uhid=lastuhid_code,
            title=title,
            gender=gender, 
            patient_name=patient_name,
            dob=dob,
            age=age,
            email_id=email_id,
            contact_number=contact_number,
            Address=Address
        )
        uhid=lastuhid_code,
        db.session.add(patient)
        db.session.commit()
    return render_template('patientregister.html',uhid=lastuhid_code)

#editpatient
@app.route('/editpatient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        # Update the patient details here based on the form data
        patient.title = request.form.get('title')
        patient.gender = request.form.get('gender')
        patient.patient_name = request.form.get('patient_name')
        patient.dob = request.form.get('dob')
        patient.age = request.form.get('age')
        patient.email_id = request.form.get('email_id')
        patient.contact_number = request.form.get('contact_number')
        patient.status = request.form.get('status')
        
        db.session.commit()
        return redirect('/')  # Redirect to the patient registration summary page

    return render_template('editpatient.html', patient=patient)

@app.route('/deletepatient/<int:patient_id>', methods=['GET', 'POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return redirect('/')
   

@app.route('/', methods=['GET', 'POST'])
def summary():
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        patient_name = request.form.get('patient_name')

        # Check if the date strings are not empty before converting
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None

        # Perform the search using the provided parameters
        # Modify this query based on your data model and search criteria
        query = Patient.query

        if start_date:
            query = query.filter(Patient.current_date >= start_date)
        if end_date:
            query = query.filter(Patient.current_date <= end_date)
        if patient_name:
            query = query.filter(Patient.patient_name.ilike(f"%{patient_name}%"))

        results = query.all()

        visit_results = Visit.query.all()  # You might want to add search criteria for visits

        return render_template('registrationsummary.html', patient=results, visit=visit_results)

    # If the request is not a POST request, show all records
    patient = Patient.query.all()
    visit = Visit.query.all()

    # if g you want to retrieve all values in the 'template' column in generatereport
    all_visitid = generatereport.query.with_entities(generatereport.visitid).all()

    print(all_visitid)
    
    visitids=[i[0] for i in all_visitid]
    print(visitids)

    return render_template('registrationsummary.html', patient=patient, visit=visit,visitids=visitids)


# testmaster
@app.route('/testmaster', methods=['GET', 'POST'])
def testmaster():
    if request.method == 'POST':
        testname = request.form.get('testname')
        specimentype = request.form.get('specimentype')

        query = Testmaster.query

        if testname:
            query = query.filter(Testmaster.testname.ilike(f"%{testname}%"))

        if specimentype:
            query = query.filter(Testmaster.specimentype.ilike(f"%{specimentype}%"))

        test = query.all()

        return render_template('tests-master.html', test=test)

    # If the request is not a POST request, show all records
    test = Testmaster.query.all()
    return render_template('tests-master.html', test=test)
    
  
    
#addtest
@app.route('/addtest', methods=['GET', 'POST'])
def addtest():
        # Generate a unique testcode (e.g., T00001, T00002, ...)
    next_code=''
    last_testmaster = Testmaster.query.order_by(Testmaster.id.desc()).first()
    if last_testmaster:
        last_code = int(last_testmaster.testcode[1:])
        next_code = f'T{last_code + 1:05}'
    else:
        next_code = 'T00001'
    if request.method == 'POST':
        testname = request.form.get('testname')
        specimentype = request.form.get('specimentype')


        
        testmaster = Testmaster(
            testcode=next_code,
            testname=testname,
            specimentype=specimentype,
        )
        testcode=next_code
        
        db.session.add(testmaster)
        db.session.commit()

    return render_template('addtest.html',code=next_code)

#edittest
@app.route('/edittest/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    test = Testmaster.query.get_or_404(test_id)
    
    if request.method == 'POST':
        # Update the patient details here based on the form data
        test.testcode = request.form.get('testcode')
        test.testname = request.form.get('testname')
        test.specimentype = request.form.get('specimentype')
                
        db.session.commit()
        return redirect('/')  # Redirect to the patient registration summary page

    return render_template('edittest.html', test=test)

#deletetest
@app.route('/deletetest/<int:test_id>', methods=['GET', 'POST'])
def delete_test(test_id):
    test = Testmaster.query.get_or_404(test_id)
    db.session.delete(test)
    db.session.commit()
    return redirect('/')
   



#refdrmaster
@app.route('/refdrmaster',methods=['GET','POST'])
def refdrmaster():
    if request.method == 'POST':
        DoctorName = request.form.get('DoctorName')
        Qualification = request.form.get('Qualification')

        query = refdr.query

        if DoctorName:
            query = query.filter(refdr.DoctorName.ilike(f"%{DoctorName}%"))

        if Qualification:
            query = query.filter(refdr.Qualification.ilike(f"%{Qualification}%"))

        refdrs = query.all()

        return render_template('refdrmaster.html', refdrs=refdrs)

    # If the request is not a POST request, show all records
    refdrs = refdr.query.all()
    return render_template('refdrmaster.html', refdrs=refdrs)
    
    
    
#addrefdr
@app.route('/addrefdr', methods=['GET', 'POST'])
def addrefdr():
    Doclast_code=''
    last_refdrmaster = refdr.query.order_by(refdr.id.desc()).first()
    if last_refdrmaster and last_refdrmaster.DoctorCode:
        Doc_code = int(last_refdrmaster.DoctorCode[1:])
        Doclast_code = f'D{Doc_code + 1:05}'
    else:
        Doclast_code = 'D00001'
    if request.method == 'POST':
        DoctorName = request.form.get('DoctorName')
        Qualification = request.form.get('Qualification')
        Specialisation = request.form.get('Specialisation')
        Address = request.form.get('Address')
        Mobile = request.form.get('Mobile')
        

            
        refdrmaster = refdr(
            DoctorCode=Doclast_code,
            DoctorName=DoctorName,
            Qualification=Qualification,
            Specialisation=Specialisation,
            Address=Address,
            Mobile=Mobile
        )
        
        db.session.add(refdrmaster)
        db.session.commit()

    return render_template('addrefdr.html',Doclast_code=Doclast_code)

#editrefdr
@app.route('/editrefdr/<int:refdr_id>', methods=['GET', 'POST'])
def edit_refdr(refdr_id):
    refdrs = refdr.query.get_or_404(refdr_id)
    
    if request.method == 'POST':
        # Update the patient details here based on the form data
        refdrs.DoctorCode = request.form.get('DoctorCode')
        refdrs.DoctorName = request.form.get('DoctorName')
        refdrs.Qualification = request.form.get('Qualification')
        refdrs.Specialisation = request.form.get('Specialisation')
        refdrs.Address = request.form.get('Address')
        refdrs.Mobile = request.form.get('Mobile')
         
        db.session.commit()
        return redirect('/')  # Redirect to the patient registration summary page

    return render_template('editrefdr.html', refdrs=refdrs)

#deleterefdr
@app.route('/deleterefdr/<int:refdr_id>', methods=['GET', 'POST'])
def delete_refdr(refdr_id):
    refdrs = refdr.query.get_or_404(refdr_id)
    db.session.delete(refdrs)
    db.session.commit()
    return redirect('/')


#pathologistmaster
@app.route('/pathologistmaster',methods=['GET','POST'])
def pathologistmaster():
    if request.method == 'POST':
        DoctorName = request.form.get('DoctorName')
        Qualification = request.form.get('Qualification')

        query = pathologist.query

        if DoctorName:
            query = query.filter(pathologist.DoctorName.ilike(f"%{DoctorName}%"))

        if Qualification:
            query = query.filter(pathologist.Qualification.ilike(f"%{Qualification}%"))

        pathologists = query.all()

        return render_template('pathologistmaster.html', pathologists=pathologists)

    # If the request is not a POST request, show all records
    pathologists = pathologist.query.all()
    return render_template('pathologistmaster.html', pathologists=pathologists)
    
    
    
    pathologistmaster = pathologist.query.all()
    return render_template('pathologistmaster.html',pathologistmaster=pathologistmaster)  
    
#addpathologist
@app.route('/addpathologist', methods=['GET', 'POST'])
def addpathologist():
    Patholast_code=''
    last_pathologistmaster = pathologist.query.order_by(pathologist.id.desc()).first()
    if last_pathologistmaster and last_pathologistmaster.DoctorCode:
        Patho_code = int(last_pathologistmaster.DoctorCode[1:])
        Patholast_code = f'P{Patho_code + 1:05}'
    else:
        Patholast_code = 'P00001'
    if request.method == 'POST':
        DoctorName = request.form.get('DoctorName')
        Qualification = request.form.get('Qualification')
        Specialisation = request.form.get('Specialisation')
        Address = request.form.get('Address')
        Mobile = request.form.get('Mobile')
        
        # Assuming 'signature' is the name attribute of your file input
        signature_file = request.files['signature']
        file_name=signature_file.filename
        print(file_name)
        # Save the uploaded file to a folder (you can customize the folder)
        path=f'static/signatures/{file_name}'
        signature_file.save(path)
        

        
        Pathologist = pathologist(
            DoctorCode=Patholast_code,
            DoctorName=DoctorName,
            Qualification=Qualification,
            Specialisation=Specialisation,
            Address=Address,
            Mobile=Mobile,
            signature='/'+path
            
             
        )
        db.session.add(Pathologist)
        db.session.commit()

    return render_template('addpathologist.html',Patholast_code=Patholast_code)

#editpathologist
@app.route('/editpathologist/<int:pathologist_id>', methods=['GET', 'POST'])
def edit_pathologist(pathologist_id):
    pathologists = pathologist.query.get_or_404(pathologist_id)
    
    if request.method == 'POST':
        # Update the patient details here based on the form data
        pathologists.DoctorCode = request.form.get('DoctorCode')
        pathologists.DoctorName = request.form.get('DoctorName')
        pathologists.Qualification = request.form.get('Qualification')
        pathologists.Specialisation = request.form.get('Specialisation')
        pathologists.Address = request.form.get('Address')
        pathologists.Mobile = request.form.get('Mobile')
        pathologists.signature = request.form.get('signature')
         
        db.session.commit()
        return redirect('/')  # Redirect to the patient registration summary page

    return render_template('editpathologist.html', pathologists=pathologists)

#deleterefdr
@app.route('/deletepathologist/<int:pathologist_id>', methods=['GET', 'POST'])
def delete_pathologist(pathologist_id):
    pathologists = pathologist.query.get_or_404(pathologist_id)
    db.session.delete(pathologists)
    db.session.commit()
    return redirect('/')

#reportformat
@app.route('/reportformat',methods=['GET','POST'])
def Reportformat():
    Reportformat = reportformat.query.all()
    return render_template('reportformat.html',Reportformat=Reportformat)  
    
#addreport
@app.route('/addreport', methods=['GET', 'POST'])
def addreport():
    if request.method == 'POST':
        Code = request.form.get('Code')
        reportname = request.form.get('reportname')
        template = request.form.get('template')
        Reportformat = reportformat(
            Code=Code,
            reportname=reportname,
            template=template, 
        )
        db.session.add(Reportformat)
        db.session.commit()

    return render_template('addreport.html')

#editreport
@app.route('/editreport/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    reports = reportformat.query.get_or_404(report_id)
    
    if request.method == 'POST':
        # Update the patient details here based on the form data
        reports.Code = request.form.get('Code')
        reports.reportname = request.form.get('reportname')
        reports.template = request.form.get('template')
       
        db.session.commit()
        return redirect('/')  # Redirect to the patient registration summary page

    return render_template('editreport.html', reports=reports)

#deletereport
@app.route('/deletereport/<int:report_id>', methods=['GET', 'POST'])
def delete_report(report_id):
    report = reportformat.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return redirect('/')

# generatereport route
@app.route('/generatereport/<int:visit_id>', methods=['GET', 'POST'])
def generatereports(visit_id):
    # Use distinct variable names for clarity
    visit = Visit.query.get_or_404(visit_id)
    pathologists = pathologist.query.all()
    patients = Patient.query.all()  # Change the variable name to 'patients'
    templates = reportformat.query.all()  # Change the variable name to 'templates'
    

    if request.method == 'POST':
        if request.form.get('hidd')=='valuechanged':
            pathologistid = request.form.get('pathologistid')
            templateid=request.form.get('templateid')
            temp = reportformat.query.get_or_404(templateid)

            return render_template('generatereport.html',
                           pathologists=pathologists,
                           visit=visit,  # Change the variable name to 'visit'
                           patients=patients,  # Change the variable name to 'patients'
                           templates=templates,  # Change the variable name to 'templates'
                           temp=temp,
                           templateid=int(templateid),
                           pathologistid=pathologistid
    
                           )
        else:
            
            pathologistid = request.form.get('pathologistid')
            patientname = request.form.get('patientname')
            templateid = request.form.get('templateid')
            template = request.form.get('template')
            visitid=request.form.get('visitid')
            
            
            generatereports = generatereport(
             
                pathologistid=pathologistid,
                patientname=patientname,
                templateid=templateid,
                template=template,
                visitid=visitid
            )
            db.session.add(generatereports)
            db.session.commit()

    return render_template('generatereport.html',
                           pathologists=pathologists,
                           visit=visit,  # Change the variable name to 'visit'
                           patients=patients,  # Change the variable name to 'patients'
                           templates=templates,  # Change the variable name to 'templates'
                           temp=None
                           )


#addvisit
@app.route('/addvisit/<int:patient_id>', methods=['GET', 'POST'])
def addvisit(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    refdrs = refdr.query.all()
    selecttest = Testmaster.query.all()
    if request.method == 'POST':
        uhid = request.form.get('uhid')
        title = request.form.get('title')
        gender = request.form.get('gender')
        patient_name= request.form.get('patient_name')
        dob= request.form.get('dob')
        age= request.form.get('age')
        email_id= request.form.get('email_id')
        contact_number= request.form.get('contact_number')
        Address= request.form.get('Address')
        ref_dr = request.form.get('ref_dr')
        select_test = request.form.get('select_test')
        
        
        visitmaster = Visit.query.order_by(Visit.id.desc()).first()
        if visitmaster and visitmaster.visitid:
            visit_code = int(visitmaster.visitid[1:])
            lastvisit_code = f'V{visit_code + 1:05}'
        else:
            lastvisit_code = 'V00001'
        
        visit = Visit(
            visitid=lastvisit_code,
            uhid=uhid,
            title=title,
            gender=gender, 
            patient_name=patient_name,
            dob=dob,
            age=age,
            email_id=email_id,
            contact_number=contact_number,
            Address=Address,
            ref_dr=ref_dr,
            select_test=select_test
        )
        db.session.add(visit)
        db.session.commit()
    
    return render_template('addvisit.html',patient=patient,refdrs=refdrs,selecttest=selecttest)

#editvisit
@app.route('/editvisit/<int:visit_id>', methods=['GET', 'POST'])
def edit_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    
    if request.method == 'POST':
        # Update the patient details here based on the form data
        visit.uhid = request.form.get('uhid')
        visit.title = request.form.get('title')
        visit.gender = request.form.get('gender')
        visit.patient_name= request.form.get('patient_name')
        visit.dob= request.form.get('dob')
        visit.age= request.form.get('age')
        visit.email_id= request.form.get('email_id')
        visit.contact_number= request.form.get('contact_number')
        visit.ref_dr = request.form.get('ref_dr')
        visit.select_test = request.form.get('select_test')
        visit.Address = request.form.get('Address')
        
        db.session.commit()
        return redirect('/')  # Redirect to the patient registration summary page

    return render_template('editvisit.html', visit=visit)

#deletevisit
@app.route('/deletevisit/<visit_id>', methods=['GET', 'POST'])
def delete_visit(visit_id):
    visit =  Visit.query.filter_by(visitid=visit_id).first_or_404()
    report=generatereport.query.filter_by(visitid=visit_id).first()
    db.session.delete(visit)
    if report!=None:
        db.session.delete(report)
    db.session.commit()
    return redirect('/')
    
@app.route('/generate_qrcode_pdf/<int:visit_id>')
def generate_qrcode_pdf(visit_id):
    # Assuming you have a Visit object with the specified visit_id
    visit = Visit.query.get_or_404(visit_id)

    # Combine relevant information into a string
    data = f"ID: {visit.id}\nUHID: {visit.uhid}\nvisitid: {visit.visitid}\npatient_name: {visit.title} {visit.patient_name}\ngender: {visit.gender}\nDOB: {visit.dob}\nAge: {visit.age}\nEmailid: {visit.email_id}\ncontact_number: {visit.contact_number}\nAddress: {visit.Address}\nRef_dr: {visit.ref_dr}\nselectedtest: {visit.select_test}"

    # Generate QR code with box_size set to 15
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=15,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Create a PDF response
    pdf_buffer = BytesIO()
    pdf_canvas = canvas.Canvas(pdf_buffer)

    # Draw the QR code onto the PDF
    pdf_canvas.drawInlineImage(img, 100, 500, width=25, height=25)  # Adjust placement and size

    # Additional information can be added to the PDF if needed
    pdf_canvas.drawString(100, 450, f"Visit ID: {visit.id}")

    pdf_canvas.save()

    # Set up response headers
    response = Response(pdf_buffer.getvalue(), content_type='application/pdf')
    response.headers['Content-Disposition'] = f'inline; filename=qr_code_visit_{visit.id}.pdf'

    return response

@app.route('/generate_barcode_pdf/<int:visit_id>')
def generate_barcode_pdf(visit_id):
    # Assuming you have a Visit object with the specified visit_id
    visit = Visit(visit_id)

    # Generate barcode image using python-barcode
    buffer = BytesIO()
    code128 = Code128(str(visit.id), writer=ImageWriter())
    code128.save(buffer)
    barcode_image = buffer.getvalue()

    # Generate PDF using reportlab
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    # Add content to the PDF
    pdf.drawString(100, 750, f'Visit ID: {visit.id}')
    
    # Draw the barcode image on the PDF
    pdf.drawImage(BytesIO(barcode_image), 100, 600, width=200, height=100)

    # Save the PDF to the buffer
    pdf.save()

    # Return the PDF as a response
    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=barcode_{visit.id}.pdf'

    return response

@app.route('/printreport/<visit_id>')
def generate_print_report(visit_id):
    visit = Visit.query.filter_by(visitid=visit_id).first_or_404()
    template = generatereport.query.filter_by(visitid=visit_id).first_or_404()
    pathologistid = template.pathologistid
    pathologists = pathologist.query.filter_by(DoctorCode=pathologistid).first_or_404()
    html = render_template('report.html', visit=visit, template=template, pathologists=pathologists)

    pdf_buffer = io.BytesIO()
    base_url = request.url_root  # or set it manually
    pisa.CreatePDF(io.StringIO(html), pdf_buffer, path=base_url)
    pdf_buffer.seek(0)

    return send_file(pdf_buffer, download_name='output.pdf', as_attachment=True)
   # p=pisa.CreatePDF(html)
    # pdf=p.dest.getvalue()

    # response = make_response(pdf)
    # response.headers['Content-Type'] = 'application/pdf'
    # response.headers['Content-Disposition'] = f'inline; filename=output_{visit.id}.pdf'

    # return response


#addrouter
@app.route('/addrouter', methods=['GET', 'POST'])
def addrouter():
    if request.method == 'POST':
        aetitle = request.form.get('aetitle')
        ipaddress = request.form.get('ipaddress')
        portnumber = request.form.get('portnumber')
        routers = router(
           aetitle=aetitle,
           ipaddress=ipaddress,
           portnumber = portnumber,
        )
        db.session.add(routers)
        db.session.commit()
    routers = router.query.all()   
    return render_template('router.html',routers=routers)   


@app.route('/previewreport/<visit_id>')
def generate_preview_report(visit_id):
    visit =  Visit.query.filter_by(visitid=visit_id).first_or_404()
    template = generatereport.query.filter_by(visitid=visit_id).first_or_404() 
    pathologistid=template.pathologistid
    pathologists=pathologist.query.filter_by(DoctorCode=pathologistid).first_or_404()
    return render_template('report.html',visit=visit,template=template,pathologists=pathologists)


  
       
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)





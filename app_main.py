from flask import Flask, render_template, request, redirect, Markup
import app_model as m # Import the model functions and variables

app = Flask(__name__)

@app.route("/")
def index():
    ## print the home page
    return render_template("home.html")

@app.route("/displaylist",methods=["POST"])
def displaylist():
    if request.form["browseby"] == 'title':
        col_head = ['Game Title','Rating','Weight']
    elif request.form["browseby"] == 'designer':
        col_head = ['Designer Name','Average Rating of Games','Average Weight of Games']
    elif request.form["browseby"] == 'publisher':
        col_head = ['Publisher Name','Average Rating of Games','Average Weight of Games']
    choice = request.form["browseby"] # Keep the request format of this variable above for readability.

    tabledata = m.get_plot_data(choice)
    plot_div = m.create_plotly(tabledata)

    return render_template("table.html",col_head=col_head,datalist=tabledata,plot=Markup(plot_div))




if __name__=="__main__":
    #app_model.init()
    app.run(debug=True)

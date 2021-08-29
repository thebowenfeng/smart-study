import React, { Component, componentDidMount} from 'react';
import Chart from 'react-apexcharts';
import axios from 'axios';
import Cookies from 'js-cookie';
import jwt_decode from "jwt-decode";

var id = Cookies.get("id_token")
var username = ""
if(id !== undefined) {
    username = jwt_decode(id)["username"]
}
var token = Cookies.get("access_token");
var refresh = Cookies.get("refresh_token");

//console.log(this.state.data)
async function refreshAccessToken() {
    let json = JSON.stringify({"ClientID": "react", "ClientSecret": "my secret", "RefreshToken": refresh});
    let response = await axios.post(' https://auth-smartstudy.herokuapp.com/refresh_access_token', json,{
        headers: {
            "Content-Type": "application/json"
        }
    })
    var access_token = response.data["access_token"];
    var refresh_token = response.data["refresh_token"];
    var id_token = response.data["id_token"];

    Cookies.set('access_token', access_token, { path: '/'});
    Cookies.set('refresh_token', refresh_token, { path: '/'});
    Cookies.set('id_token', id_token, { path: '/'});
    console.log("Refreshed token to " + refresh_token)

    token = Cookies.get("access_token");
    id = Cookies.get("id_token");
    refresh = Cookies.get("refresh_token");
}
class PieChart extends React.Component {
    constructor(props) {
        super(props);

        this.state = {

            series: [],
            options: {
                chart: {
                    width: 380,
                    type: 'pie',
                },
                theme: {
                    mode: 'light',
                    palette: 'palette4',
                },
                labels: [],
                responsive: [{
                    breakpoint: 480,
                    options: {
                        chart: {
                            width: 400
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }]
            },


        };
    }

    updateCharts(label, data) {
        let newOptions = {
            chart: {
                width: 380,
                type: 'pie',
            },
            theme: {
                mode: 'light',
                palette: 'palette4',
            },
                labels: [],
            responsive: [{
                breakpoint: 480,
                options: {
                    chart: {
                        width: 400
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }]
        };
        let newSeries = [];

        newOptions.labels = label;
        newSeries = data;

        this.setState({
            series: newSeries,
            options: newOptions,
        });
    }


    componentDidMount() {
        (async () => {
            // Refresh every time lmao
            await refreshAccessToken()
            var json = JSON.stringify({"Username": username});
            console.log(username)
            let res = await axios.post('https://resource-smartstudy.herokuapp.com/get_website_data', json, {
                headers: {
                    "Content-Type": 'application/json',
                    "Authorization": `${token}`
                }
            })
            console.log(res)
            var arr_key = []
            var arr_val = []
            for (var key in res.data) {
                arr_val.push(parseInt(res.data[key]));
                arr_key.push(key)
            }
            this.updateCharts(arr_key, arr_val);
            //this.state.series[0].data = arr_val;
            //this.state.options.xaxis.categories = arr_key;
            console.log(this.state.series);
            console.log(this.state.options.labels)
        })()

    }

    render() {
        return (


            <div id="chart">
                <Chart options={this.state.options} series={this.state.series} type="pie" width={500} />
            </div>


        );
    }
}

export default PieChart;
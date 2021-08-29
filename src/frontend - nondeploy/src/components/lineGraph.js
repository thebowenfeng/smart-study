import React, { Component, componentDidMount } from "react";
import Chart from "react-apexcharts";
import axios from "axios";
import Cookies from "js-cookie";
import jwt_decode from "jwt-decode";
import "./lineGraph-style.css";
import PieChart from "./PieChart";
import PieApp from "./PieChart-App";
import Scores from "./Scores";

var id = Cookies.get("id_token");
var username = "";
if (id !== undefined) {
    username = jwt_decode(id)["username"];
}
var token = Cookies.get("access_token");
var refresh = Cookies.get("refresh_token");

//console.log(this.state.data)
async function refreshAccessToken() {
    let json = JSON.stringify({
        ClientID: "react",
        ClientSecret: "my secret",
        RefreshToken: refresh,
    });
    let response = await axios.post(
        " https://auth-smartstudy.herokuapp.com/refresh_access_token",
        json,
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
    var access_token = response.data["access_token"];
    var refresh_token = response.data["refresh_token"];
    var id_token = response.data["id_token"];

    Cookies.set("access_token", access_token, { path: "/" });
    Cookies.set("refresh_token", refresh_token, { path: "/" });
    Cookies.set("id_token", id_token, { path: "/" });
    console.log("Refreshed token to " + refresh_token);

    token = Cookies.get("access_token");
    id = Cookies.get("id_token");
    refresh = Cookies.get("refresh_token");
}

class lineGraph extends Component {
    constructor(props) {
        super(props);

        this.updateCharts = this.updateCharts.bind(this);

        this.state = {
            options: {
                stroke: {
                    curve: "smooth",
                },
                markers: {
                    size: 0,
                },
                yaxis: {
                    min: 0,
                    max: 1,
                    title: {
                        text: "Scores",
                        rotate: -90,
                        offsetX: 0,
                        offsetY: 0,
                        style: {
                            color: '#695d5d',
                            fontSize: '12px',
                            fontFamily: 'Helvetica, Arial, sans-serif',
                            fontWeight: 600,
                            cssClass: 'apexcharts-yaxis-title',
                        },
                    }
                },
                xaxis: {
                    categories: [],
                    title: {
                        text: "Timestamps (seconds)",
                        offsetX: 0,
                        offsetY: 0,
                        style: {
                            color: '#695d5d',
                            fontSize: '12px',
                            fontFamily: 'Helvetica, Arial, sans-serif',
                            fontWeight: 600,
                            cssClass: 'apexcharts-xaxis-title',
                        },
                    }
                },

                fill:{
                    colors: ['#61c7c8'],
                },
            },
            series: [
                {
                    data: [],
                },
            ],
            data: {},
        };
    }

    updateCharts(label, data) {
        const newOptions = {
            stroke: {
                curve: "smooth",
            },
            markers: {
                size: 0,
            },
            yaxis: {
                min: 0,
                max: 1,
                title: {
                    text: "Scores",
                    rotate: -90,
                    offsetX: 0,
                    offsetY: 0,
                    style: {
                        color: '#695d5d',
                        fontSize: '12px',
                        fontFamily: 'Helvetica, Arial, sans-serif',
                        fontWeight: 600,
                        cssClass: 'apexcharts-yaxis-title',
                    },
                }
            },
            xaxis: {
                categories: [],
                title: {
                    text: "Timestamps (seconds)",
                    offsetX: 0,
                    offsetY: 0,
                    style: {
                        color: '#695d5d',
                        fontSize: '12px',
                        fontFamily: 'Helvetica, Arial, sans-serif',
                        fontWeight: 600,
                        cssClass: 'apexcharts-xaxis-title',
                    },
                }
            },
        };
        const newSeries = [
            {
                data: [],
            },
        ];

        newOptions.xaxis.categories = label;
        newSeries[0].data = data;

        this.setState({
            series: newSeries,
            options: newOptions,
        });
    }

    componentDidMount() {
        (async () => {
            // Refresh every time
            await refreshAccessToken();
            var json = JSON.stringify({ Username: username });
            console.log(username);
            let res = await axios.post(
                "https://resource-smartstudy.herokuapp.com/get_interval_scores",
                json,
                {
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `${token}`,
                    },
                }
            );
            console.log(res);
            var arr_key = [];
            var arr_val = [];
            for (var key in res.data) {
                arr_val.push(parseFloat(res.data[key]).toFixed(2));
                arr_key.push(key);
            }
            this.updateCharts(arr_key, arr_val);
            //this.state.series[0].data = arr_val;
            //this.state.options.xaxis.categories = arr_key;
            //console.log(this.state.options.xaxis.categories);
        })();
    }

    render() {
        console.log(this.state.options.xaxis.categories);
        console.log(this.state.series[0].data);
        return (
            <div className="container container-fluid">
                <div className="linechart-container container-fluid">
                    <div className="row">
                        <div className="col-sm">
                            <h3 className="title text-center">DashBoard</h3>
                            <p className="instruct3 text-center">
                                <Scores />
                            </p>
                        </div>

                        <div className="col-sm">
                            <div className="main-line">
                                <div className="line">
                                    <h3 className="title text-center">Study Session Focus Level</h3>{" "}
                                    <div className="header">

                                        <div className="chart-wrapper ">
                                            <Chart
                                                options={this.state.options}
                                                series={this.state.series}
                                                type="line"
                                                width='500'
                                            />
                                        </div>

                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="linechart-container container-fluid">
                    <div className="row">
                        <div className="col-sm">
                            <h3 className="title text-center">Application Usage</h3>

                            <div className="chart-wrapper">
                                <PieApp/>
                            </div>
                        </div>

                        <div className="col-sm">
                            <div className="main-line">
                                <div className="line">
                                    <h3 className="title text-center">Website Usage</h3>
                                    <div className="chart-wrapper">
                                        <div>
                                            <PieChart />
                                        </div>
                                    </div>{" "}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        );
    }
}

export default lineGraph;
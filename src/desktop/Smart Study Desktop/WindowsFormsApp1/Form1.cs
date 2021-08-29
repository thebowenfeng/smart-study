using Newtonsoft.Json;
using SimpleHttp;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class Login : Form
    {
        public Login()
        {
            InitializeComponent();
        }

        private void btnLogin_Click(object sender, EventArgs e)
        {
            CancellationTokenSource cancel = new CancellationTokenSource();

            Route.Add("/{Query}", async (req, res, props) =>
            {
                var payload = new Dictionary<string, string>
                {
                    { "ClientID", "react" },
                    { "ClientSecret", "my secret" },
                    { "AuthCode", req.QueryString.Get("auth_code")}
                };

                string jsonContent = JsonConvert.SerializeObject(payload);
                StringContent httpContent = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                HttpClient client = new HttpClient();
                HttpResponseMessage response = await client.PostAsync("https://auth-smartstudy.herokuapp.com/get_access_token", httpContent);

                Dictionary<string, string> tokens = JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());

                string tokenString = JsonConvert.SerializeObject(tokens);
                File.WriteAllText("token.txt", tokenString);

                res.AsText("You can safely close the page.");

                cancel.Cancel();
            });

            System.Diagnostics.Process.Start("https://auth-smartstudy.herokuapp.com/login?callback=http://localhost:1337");

            HttpServer.ListenAsync(
                1337,
                cancel.Token,
                Route.OnHttpRequestAsync
                );

            btnLogin.Visible = false;
            label1.Visible = true;
        }

        private void Login_Load(object sender, EventArgs e)
        {
            label1.Visible = false;
        }
    }
}

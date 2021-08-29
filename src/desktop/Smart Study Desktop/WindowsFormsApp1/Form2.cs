using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.IdentityModel.Tokens.Jwt;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class Main : Form
    {

        private void AdminRelauncher()
        {
            if (!IsRunAsAdmin())
            {
                ProcessStartInfo proc = new ProcessStartInfo();
                proc.UseShellExecute = true;
                proc.WorkingDirectory = Environment.CurrentDirectory;
                proc.FileName = Assembly.GetEntryAssembly().CodeBase;

                proc.Verb = "runas";

                try
                {
                    Process.Start(proc);
                    this.Close();
                }
                catch (Exception ex)
                {
                    //Console.WriteLine("This program must be run as an administrator! \n\n" + ex.ToString());
                }
            }
        }

        private bool IsRunAsAdmin()
        {
            try
            {
                WindowsIdentity id = WindowsIdentity.GetCurrent();
                WindowsPrincipal principal = new WindowsPrincipal(id);
                return principal.IsInRole(WindowsBuiltInRole.Administrator);
            }
            catch (Exception)
            {
                return false;
            }
        }
        public Main()
        {
            InitializeComponent();
            AdminRelauncher();
        }

        string readIdToken(string token)
        {
            
            JwtSecurityTokenHandler handler = new JwtSecurityTokenHandler();
            JwtSecurityToken id_token = handler.ReadJwtToken(token);

            string username = JsonConvert.DeserializeObject<Dictionary<string, string>>(id_token.Payload.SerializeToJson())["username"];
            return username;
        }

        string[] topicIndexes = {"History", "Geography", "Arts", "Philosophy/Religion","asdfasdf",
                  "Society/Social Science","Biological/Health Science", "Physical Science",
              "Technology", "Mathematics"};

        async Task<Dictionary<string, string>> sendRequest(Dictionary<string, string> httpPayload, string url)
        {
            Dictionary<string, string> tokens = JsonConvert.DeserializeObject<Dictionary<string, string>>(File.ReadAllText("token.txt"));
            string username = readIdToken(tokens["id_token"]);

            httpPayload["Username"] = username;

            string jsonContent = JsonConvert.SerializeObject(httpPayload);
            StringContent httpContent = new StringContent(jsonContent, Encoding.UTF8, "application/json");

            HttpClient client = new HttpClient();
            client.DefaultRequestHeaders.Add("Authorization", tokens["access_token"]);
            HttpResponseMessage response = await client.PostAsync(url, httpContent);

            if (response.StatusCode == System.Net.HttpStatusCode.Forbidden)
            {
                var newHttpPayload = new Dictionary<string, string>
                {
                    { "ClientID", "react"},
                    { "ClientSecret", "my secret"},
                    { "RefreshToken", tokens["refresh_token"]}
                };

                jsonContent = JsonConvert.SerializeObject(newHttpPayload);
                httpContent = new StringContent(jsonContent, Encoding.UTF8, "application/json");

                response = await client.PostAsync("https://auth-smartstudy.herokuapp.com/refresh_access_token", httpContent);
                Dictionary<string, string> newTokens = JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());

                string tokenString = JsonConvert.SerializeObject(newTokens);
                File.WriteAllText("token.txt", tokenString);
                var result = await sendRequest(httpPayload, url);
                return result;
            }
            else
            {
                return JsonConvert.DeserializeObject<Dictionary<string, string>>(await response.Content.ReadAsStringAsync());
            }
        }

        void runPython()
        {
            Dictionary<string, string> tokens = JsonConvert.DeserializeObject<Dictionary<string, string>>(File.ReadAllText("token.txt"));
            string username = readIdToken(tokens["id_token"]);

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "Python\\hello.exe";
            start.Arguments = "Python\\main.py " + tokens["access_token"] + " " + tokens["refresh_token"] + " " + username + " " + GlobalVars.cameraIndex.ToString();
            start.UseShellExecute = false;
            start.CreateNoWindow = true;

            Process process = Process.Start(start);
            process.Start();
        }

        void closePython()
        {
            Process[] runningProcesses = Process.GetProcesses();
            
            foreach (Process process in runningProcesses)
            {   
                if (process.ProcessName == "hello")
                {
                    process.Kill();
                }
                
            }
        }

        async void iterApps()
        {
            string currAppUsed = "";
            string[] disAllowed = { "winstore.app", "textinputhost", "cmd", "devenv", "video.ui", "applicationframehost", "systemsettings"};
            var processes = Process.GetProcesses().Where(p => p.MainWindowHandle != IntPtr.Zero).ToArray();
            foreach(Process process in processes)
            {
                if (process.MainWindowTitle != "" && !disAllowed.Contains(process.ProcessName.ToLower()) && process.ProcessName.ToLower() != "")
                {
                    currAppUsed += process.ProcessName + "|";
                }
            }
            var httpPayload = new Dictionary<string, string>
                {
                    { "Username", ""},
                    { "Apps", currAppUsed}
                };
            await sendRequest(httpPayload, "https://resource-smartstudy.herokuapp.com/post_app_data");
            //MessageBox.Show(JsonConvert.SerializeObject(resp));
        }

        private void Main_Load(object sender, EventArgs e)
        {
            //Load colors
            label1.ForeColor = Color.FromArgb(97, 199, 200);
            chxTopic.ForeColor = Color.FromArgb(105, 93, 93);
            tabPage1.BackColor = Color.FromArgb(235, 247, 245);

            if (File.Exists("token.txt"))
            {
                try
                {
                    Dictionary<string, string> tokens = JsonConvert.DeserializeObject<Dictionary<string, string>>(File.ReadAllText("token.txt"));
                    if (!tokens.ContainsKey("refresh_token") || !tokens.ContainsKey("access_token") || !tokens.ContainsKey("id_token"))
                    {
                        throw new Exception();
                    }

                    pictureBox2.Visible = true;
                    pictureBox3.Visible = false;
                }
                catch
                {
                    bgListener.Enabled = false;
                    MessageBox.Show("Your token file is corrupted. Please login again");
                    Login newLogin = new Login();
                    newLogin.ShowDialog();
                }
            }
            else
            {
                bgListener.Enabled = false;
                Login newLogin = new Login();
                newLogin.ShowDialog();
            }

            bgListener.Enabled = true;
            iterApps();
        }

        private async void bgListener_Tick(object sender, EventArgs e)
        {
            var httpPayload = new Dictionary<string, string>
                {
                    { "Username", ""}
                };

            
            Dictionary<string, string> response = await sendRequest(httpPayload, "https://resource-smartstudy.herokuapp.com/get_status");
            //MessageBox.Show(JsonConvert.SerializeObject(response));
            if (response["status"] == "yes")
            {
                GlobalVars.inSession = true;
            }
            else
            {
                GlobalVars.inSession = false;
            }
            

            if (GlobalVars.inSession)
            {
                iterApps();
                if (!GlobalVars.startedPython)
                {
                    runPython();
                    GlobalVars.startedPython = true;
                }
                pictureBox2.Visible = false;
                pictureBox3.Visible = true;
            }
            else
            {
                if (GlobalVars.startedPython)
                {
                    closePython();
                    GlobalVars.startedPython = false;
                }
                pictureBox2.Visible = true;
                pictureBox3.Visible = false;
            }
        }

        private void pictureBox2_MouseLeave(object sender, EventArgs e)
        {
            pictureBox2.ImageLocation = "ButtonUnclick.jpg";
        }

        private async void pictureBox2_Click(object sender, EventArgs e)
        {
            MessageBox.Show("Make sure you have properly configuered your camera in the configuration page!");

            string topicStr = "";
            foreach (var items in chxTopic.CheckedItems)
            {
                topicStr += Array.IndexOf(topicIndexes, items.ToString()).ToString();
            }

            if (topicStr == "")
            {
                MessageBox.Show("You have to select at least 1 topic of study");
            }
            else
            {
                var httpPayload = new Dictionary<string, string>
                {
                    { "Username", ""},
                    {"Topic", topicStr}
                };

                await sendRequest(httpPayload, "https://resource-smartstudy.herokuapp.com/post_topics");

                httpPayload = new Dictionary<string, string>
                {
                    { "Username", ""},
                    { "Status", "start"},
                };

                await sendRequest(httpPayload, "https://resource-smartstudy.herokuapp.com/set_session_status");

                GlobalVars.inSession = true;
                pictureBox2.Visible = false;
                pictureBox3.Visible = true;
            }
        }

        private void pictureBox3_MouseLeave(object sender, EventArgs e)
        {
            pictureBox3.ImageLocation = "StopUnclick.jpg";
        }

        private async void pictureBox3_Click(object sender, EventArgs e)
        {
            var httpPayload = new Dictionary<string, string>
                {
                    { "Username", ""},
                    { "Status", "stop"}
                };

            await sendRequest(httpPayload, "https://resource-smartstudy.herokuapp.com/set_session_status");

            GlobalVars.inSession = false;
            pictureBox2.Visible = true;
            pictureBox3.Visible = false;
        }

        private void pictureBox3_MouseEnter(object sender, EventArgs e)
        {
            pictureBox3.ImageLocation = "StopHover.jpg";
        }

        private void pictureBox2_MouseEnter(object sender, EventArgs e)
        {
            pictureBox2.ImageLocation = "ButtonHover.jpg";
        }

        private void btnCmrPlus_Click(object sender, EventArgs e)
        {
            GlobalVars.cameraIndex++;
            lblCameraIndex.Text = GlobalVars.cameraIndex.ToString();
        }

        private void btnCmrMinus_Click(object sender, EventArgs e)
        {
            if (GlobalVars.cameraIndex > 0)
            {
                GlobalVars.cameraIndex--;
                lblCameraIndex.Text = GlobalVars.cameraIndex.ToString();
            }
        }

        private void btnTest_Click(object sender, EventArgs e)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = "Python\\hello.exe";
            start.Arguments = "Python\\config.py " + GlobalVars.cameraIndex.ToString();
            start.UseShellExecute = true;

            Process process = Process.Start(start);
            process.Start();
        }
    }
}

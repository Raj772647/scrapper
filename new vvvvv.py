import os
from pyrogram import *
from pyrogram.raw.functions import messages
from pyrogram.types import Message
import re
from luhn import *
import json
import pymongo
import enums
import requests
from collections import Counter

country_codes = {
	'AD': 'Andorra',
	'AE': 'United Arab Emirates',
	'AF': 'Afghanistan',
	'AG': 'Antigua & Barbuda',
	'AI': 'Anguilla',
	'AL': 'Albania',
	'AM': 'Armenia',
	'AN': 'Netherlands Antilles',
	'AO': 'Angola',
	'AQ': 'Antarctica',
	'AR': 'Argentina',
	'AS': 'American Samoa',
	'AT': 'Austria',
	'AU': 'Australia',
	'AW': 'Aruba',
	'AZ': 'Azerbaijan',
	'BA': 'Bosnia and Herzegovina',
	'BB': 'Barbados',
	'BD': 'Bangladesh',
	'BE': 'Belgium',
	'BF': 'Burkina Faso',
	'BG': 'Bulgaria',
	'BH': 'Bahrain',
	'BI': 'Burundi',
	'BJ': 'Benin',
	'BM': 'Bermuda',
	'BN': 'Brunei Darussalam',
	'BO': 'Bolivia',
	'BR': 'Brazil',
	'BS': 'Bahama',
	'BT': 'Bhutan',
	'BU': 'Burma (no longer exists)',
	'BV': 'Bouvet Island',
	'BW': 'Botswana',
	'BY': 'Belarus',
	'BZ': 'Belize',
	'CA': 'Canada',
	'CC': 'Cocos (Keeling) Islands',
	'CF': 'Central African Republic',
	'CG': 'Congo',
	'CH': 'Switzerland',
	'CI': 'Côte D\'ivoire (Ivory Coast)',
	'CK': 'Cook Iislands',
	'CL': 'Chile',
	'CM': 'Cameroon',
	'CN': 'China',
	'CO': 'Colombia',
	'CR': 'Costa Rica',
	'CS': 'Czechoslovakia (no longer exists)',
	'CU': 'Cuba',
	'CV': 'Cape Verde',
	'CX': 'Christmas Island',
	'CY': 'Cyprus',
	'CZ': 'Czech Republic',
	'DD': 'German Democratic Republic (no longer exists)',
	'DE': 'Germany',
	'DJ': 'Djibouti',
	'DK': 'Denmark',
	'DM': 'Dominica',
	'DO': 'Dominican Republic',
	'DZ': 'Algeria',
	'EC': 'Ecuador',
	'EE': 'Estonia',
	'EG': 'Egypt',
	'EH': 'Western Sahara',
	'ER': 'Eritrea',
	'ES': 'Spain',
	'ET': 'Ethiopia',
	'FI': 'Finland',
	'FJ': 'Fiji',
	'FK': 'Falkland Islands (Malvinas)',
	'FM': 'Micronesia',
	'FO': 'Faroe Islands',
	'FR': 'France',
	'FX': 'France, Metropolitan',
	'GA': 'Gabon',
	'GB': 'United Kingdom (Great Britain)',
	'GD': 'Grenada',
	'GE': 'Georgia',
	'GF': 'French Guiana',
	'GH': 'Ghana',
	'GI': 'Gibraltar',
	'GL': 'Greenland',
	'GM': 'Gambia',
	'GN': 'Guinea',
	'GP': 'Guadeloupe',
	'GQ': 'Equatorial Guinea',
	'GR': 'Greece',
	'GS': 'South Georgia and the South Sandwich Islands',
	'GT': 'Guatemala',
	'GU': 'Guam',
	'GW': 'Guinea-Bissau',
	'GY': 'Guyana',
	'HK': 'Hong Kong',
	'HM': 'Heard & McDonald Islands',
	'HN': 'Honduras',
	'HR': 'Croatia',
	'HT': 'Haiti',
	'HU': 'Hungary',
	'ID': 'Indonesia',
	'IE': 'Ireland',
	'IL': 'Israel',
	'IN': 'India',
	'IO': 'British Indian Ocean Territory',
	'IQ': 'Iraq',
	'IR': 'Islamic Republic of Iran',
	'IS': 'Iceland',
	'IT': 'Italy',
	'JM': 'Jamaica',
	'JO': 'Jordan',
	'JP': 'Japan',
	'KE': 'Kenya',
	'KG': 'Kyrgyzstan',
	'KH': 'Cambodia',
	'KI': 'Kiribati',
	'KM': 'Comoros',
	'KN': 'St. Kitts and Nevis',
	'KP': 'Korea, Democratic People\'s Republic of',
	'KR': 'Korea, Republic of',
	'KW': 'Kuwait',
	'KY': 'Cayman Islands',
	'KZ': 'Kazakhstan',
	'LA': 'Lao People\'s Democratic Republic',
	'LB': 'Lebanon',
	'LC': 'Saint Lucia',
	'LI': 'Liechtenstein',
	'LK': 'Sri Lanka',
	'LR': 'Liberia',
	'LS': 'Lesotho',
	'LT': 'Lithuania',
	'LU': 'Luxembourg',
	'LV': 'Latvia',
	'LY': 'Libyan Arab Jamahiriya',
	'MA': 'Morocco',
	'MC': 'Monaco',
	'MD': 'Moldova, Republic of',
	'MG': 'Madagascar',
	'MH': 'Marshall Islands',
	'ML': 'Mali',
	'MN': 'Mongolia',
	'MM': 'Myanmar',
	'MO': 'Macau',
	'MP': 'Northern Mariana Islands',
	'MQ': 'Martinique',
	'MR': 'Mauritania',
	'MS': 'Monserrat',
	'MT': 'Malta',
	'MU': 'Mauritius',
	'MV': 'Maldives',
	'MW': 'Malawi',
	'MX': 'Mexico',
	'MY': 'Malaysia',
	'MZ': 'Mozambique',
	'NA': 'Namibia',
	'NC': 'New Caledonia',
	'NE': 'Niger',
	'NF': 'Norfolk Island',
	'NG': 'Nigeria',
	'NI': 'Nicaragua',
	'NL': 'Netherlands',
	'NO': 'Norway',
	'NP': 'Nepal',
	'NR': 'Nauru',
	'NT': 'Neutral Zone (no longer exists)',
	'NU': 'Niue',
	'NZ': 'New Zealand',
	'OM': 'Oman',
	'PA': 'Panama',
	'PE': 'Peru',
	'PF': 'French Polynesia',
	'PG': 'Papua New Guinea',
	'PH': 'Philippines',
	'PK': 'Pakistan',
	'PL': 'Poland',
	'PM': 'St. Pierre & Miquelon',
	'PN': 'Pitcairn',
	'PR': 'Puerto Rico',
	'PT': 'Portugal',
	'PW': 'Palau',
	'PY': 'Paraguay',
	'QA': 'Qatar',
	'RE': 'Réunion',
	'RO': 'Romania',
	'RU': 'Russian Federation',
	'RW': 'Rwanda',
	'SA': 'Saudi Arabia',
	'SB': 'Solomon Islands',
	'SC': 'Seychelles',
	'SD': 'Sudan',
	'SE': 'Sweden',
	'SG': 'Singapore',
	'SH': 'St. Helena',
	'SI': 'Slovenia',
	'SJ': 'Svalbard & Jan Mayen Islands',
	'SK': 'Slovakia',
	'SL': 'Sierra Leone',
	'SM': 'San Marino',
	'SN': 'Senegal',
	'SO': 'Somalia',
	'SR': 'Suriname',
	'ST': 'Sao Tome & Principe',
	'SU': 'Union of Soviet Socialist Republics (no longer exists)',
	'SV': 'El Salvador',
	'SY': 'Syrian Arab Republic',
	'SZ': 'Swaziland',
	'TC': 'Turks & Caicos Islands',
	'TD': 'Chad',
	'TF': 'French Southern Territories',
	'TG': 'Togo',
	'TH': 'Thailand',
	'TJ': 'Tajikistan',
	'TK': 'Tokelau',
	'TM': 'Turkmenistan',
	'TN': 'Tunisia',
	'TO': 'Tonga',
	'TP': 'East Timor',
	'TR': 'Turkey',
	'TT': 'Trinidad & Tobago',
	'TV': 'Tuvalu',
	'TW': 'Taiwan, Province of China',
	'TZ': 'Tanzania, United Republic of',
	'UA': 'Ukraine',
	'UG': 'Uganda',
	'UM': 'United States Minor Outlying Islands',
	'US': 'United States of America',
	'UY': 'Uruguay',
	'UZ': 'Uzbekistan',
	'VA': 'Vatican City State (Holy See)',
	'VC': 'St. Vincent & the Grenadines',
	'VE': 'Venezuela',
	'VG': 'British Virgin Islands',
	'VI': 'United States Virgin Islands',
	'VN': 'Viet Nam',
	'VU': 'Vanuatu',
	'WF': 'Wallis & Futuna Islands',
	'WS': 'Samoa',
	'YD': 'Democratic Yemen (no longer exists)',
	'YE': 'Yemen',
	'YT': 'Mayotte',
	'YU': 'Yugoslavia',
	'ZA': 'South Africa',
	'ZM': 'Zambia',
	'ZR': 'Zaire',
	'ZW': 'Zimbabwe',
	'ZZ': 'Unknown or unspecified country',
}

# client = pymongo.MongoClient("mongodb+srv://rajveer6053:Raj7726821605@cluster0.ktunb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

client = pymongo.MongoClient("mongodb+srv://rajveer6053:Raj7726821605@cluster0.ktunb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client.credit_cards
chat_id="-1002354281978"
# chat_id = "-1002354281978"
admins =["-1002354281978","-1002354281978",916264684,6389955589]
bins=[]
linked=[]
d=[]

premium_list=[]



false=False
true=True
bot = Client(
    "MY_first_project",
    api_id=23181335,  # Replace with your valid API ID
    api_hash="b73ae83eab9abcc69449039344b0e73a",  # Replace with your valid API Hash
    bot_token="7798211459:AAGxzwQVjGyXyEmLeinfskzOAqIAg8t-X7A"  # Replace with your valid Bot Token
)

app = Client(
    name="me",
    api_id=23181335,
    api_hash="b73ae83eab9abcc69449039344b0e73a"
)
#Start message
@bot.on_message(filters.command('start') & filters.private)
def command1(bot, message):

    bot.send_message(message.chat.id, "Heya, I am a simple test bot.")
#help cmd
@bot.on_message(filters.command('help'))
def command2(bot,message):
    
    message.reply_text("HELP IS ON THE WAY")
     
#welcome text for new joiner
group=""#"add the numbers here"#grp id/username
"+18542207696"

@bot.on_message(filters.chat(group)&filters.new_chat_members)
def welcomebot(client,message):
    message.reply_text("Welcome")

  
#send photo
@bot.on_message(filters.command('join')& filters.private)
async def joinchat(Client,message):
  print(message)
  global linked
  mess=eval(str(message))
  tet=(mess["text"]).split(" ",1)
  userr = mess["from_user"]["id"]
  try:
    try:
      await app.join_chat(tet[-1])
      linked.append(tet[-1])
      print(linked)
      text = "Joined Successfully!"
      await bot.send_message(chat_id=userr, text=text)
    except Exception as e:
      print(e)
      tt=tet[-1].split("https://t.me/")
      linkk="@{}".format(tt[-1])
      await app.join_chat(linkk)
      print(linkk)
      text = "Joined Successfully!"
      await bot.send_message(chat_id=userr, text=text)
    
  except Exception as e:
    text = "The user is already a participant of this chat"
    print(e)
    await bot.send_message(chat_id=userr, text=text)

    
#maxed bin
@bot.on_message(filters.command("max"))
async def maxbin(Client,message):
  global bins
  bins_count_text=[]
  mess=eval(str(message))
  group_use = mess["from_user"]["id"]
  userr = mess["chat"]["id"]
  if userr in admins or group_use in admins:
    c = Counter(bins)
    p=(c.most_common(20))
    for i in range(len(p)):
      binn=p[i][0]
      ctr=p[i][1]
      z="<b>Top-</b>{} : <b>Bin -</b><code>{}</code> : <b>Count - </b><code>{}</code>".format(i+1,binn,ctr)
      bins_count_text.append(z)
      test_text="\n".join(bins_count_text)
    await bot.send_message(chat_id=userr, text=test_text)
  else: 
    text = "Not Authorized!"
    await bot.send_message(chat_id=userr, text=text)





    
#maxed bin
@bot.on_message(filters.command("scrape"))
async def scrape(Client, message):
    global bins
    ctr = 0
    count = 0
    mess = eval(str(message))
    userr = mess["chat"]["id"]
    
    if userr not in premium_list and userr not in admins:
        await bot.send_message(chat_id=userr, text="Not Authorized!")
        return
        
    try:
        # Parse command arguments
        args = message.text.split()
        
        if len(args) < 3:
            await bot.send_message(chat_id=userr, text="Usage: /scrape <bin> <count> [channel]")
            return
            
        binz = args[1]
        t_count = int(args[2])
        cha = args[3] if len(args) > 3 else "scrapperelexa"
        
        a_m = await bot.send_message(chat_id=message.chat.id, text="𝑳𝒐𝒂𝒅𝒊𝒏𝒈 ⬡⬡⬡")
        
        # Rest of scraping logic...
        file = open(f"{binz}_{cha}.txt", "w")
        
        async for i in app.get_chat_history(cha):
            # Existing scraping code...
            pass
            
    except Exception as e:
        await bot.send_message(chat_id=userr, text=f"Error: {str(e)}")
        return









    
#maxed bin
@bot.on_message(filters.command("groups"))
async def groups(Client,message):
  global chatgroups
  mess=eval(str(message))
  group_use = mess["from_user"]["id"]
  userr = mess["chat"]["id"]
  if userr in admins or group_use in admins:
    for i in chatgroups:
      text=chatgroups[i]
      linked.append(text)
      
      await bot.send_message(chat_id=group_use, text=text)
      print(linked)
  else:
    text = "Not Authorized!"
    await bot.send_message(chat_id=userr, text=text)


@app.on_raw_update()
async def raw(client, update, users, chats):
    try:
        p = (eval(str(update)))
        
        # Skip if message field doesn't exist
        if 'message' not in p or 'message' not in p['message']:
            return
            
        textt = (p['message']['message'])
        textt = textt.lower()
        te = textt.replace("a","").replace(":"," ").replace("b","").replace("c","").replace("d","").replace("e","").replace("f","").replace("g","").replace("h","").replace("i","").replace("j","").replace("k","").replace("l","").replace("m","").replace("n","").replace("o","").replace("p","").replace("q","").replace("r","").replace("s","").replace("t","").replace("u","").replace("v","").replace("w","").replace("x","").replace("y","").replace("z","").replace("#","").replace("@","").replace("$","").replace(";","").replace("=","").replace("+","").replace("-","").replace(".","").replace("?","").replace("%","").replace("\n"," ")
        t = re.sub(' +', ' ', te)
        rawdata = (t)

        # Try to find credit card numbers
        filtron = "[0-9]{16}[|][0-9]{1,2}[|][0-9]{2,4}[|][0-9]{3}"
        filtroa = "[0-9]{15}[|][0-9]{1,2}[|][0-9]{2,4}[|][0-9]{4}"
        cvv_num = "[0-9]{16}[ ][0-9]{3}[ ][0-9]{1,2}[/][0-9]{2,4}"
        cc_num = "[0-9]{16}[ ][0-9]{1,2}[/][0-9]{2,4}[ ][0-9]{3}"
        cc1_num = "[0-9]{16}[ ][0-9]{1,2}[ ][0-9]{2,4}[ ][0-9]{3}"
        
        # First try to find 16 digit card
        card_match = None
        card_type = None
        
        visa_match = re.findall("[0-9]{16}", rawdata)
        if visa_match:
            card_match = visa_match[0]
            card_type = card_match[0]
        else:
            # Try 15 digit amex
            amex_match = re.findall("[0-9]{15}", rawdata)
            if amex_match:
                card_match = amex_match[0]
                card_type = card_match[0]
                
        if not card_match:
            return
            
        # Extract full card details based on type
        if card_type == "3":
            x = re.findall(filtroa, rawdata)[0]
        elif card_type in ["4", "5", "6"]:
            try:
                x = re.findall(filtron, rawdata)[0]
            except:
                try:
                    x = re.findall(cc_num, rawdata)[0]
                except:
                    try:
                        x = re.findall(cc1_num, rawdata)[0]
                    except:
                        x = re.findall(cvv_num, rawdata)[0]
                        
        x = x.replace(" ","|").replace("/","|")
        
        # Check if card already exists in DB
        check_if_cc = db.credit_card.find_one({'cc_num': x.split("|")[0]})
        try:
            card_exist_indb = str(check_if_cc['cc_num'])
            existe = True
        except:
            existe = False

        check_luhn = True

        if existe is False and check_luhn is True:
            cc_data = {
                "bin": x.split("|")[0][:6],
                "cc_full": x,
                "cc_num": x.split("|")[0]
            }
              
            bin_1 = str(x)[:6]
            bins.append(bin_1)
            db.credit_card.insert_one(cc_data)
            
            try:
                r = requests.get("https://lookup.binlist.net/" + bin_1)
                if r.status_code == 200:
                    url = r.text
                    res = json.loads(url)
                    try:
                        country_bin = res["country"]["name"]
                    except:
                        country_bin = ""
                    try:
                        country_flag = res["country"]["emoji"]
                    except:
                        country_flag = ""
                    try:
                        scheme = str(res["scheme"]).title()
                    except:
                        scheme = ""
                    try:
                        type = "-"+str(res["type"]).title()
                    except:
                        type = ""
                    try:
                        brand = "-"+str(res["brand"]).title()
                    except:
                        brand = ""
                    try:
                        bankk = str(res["bank"]["name"]).title()
                    except:
                        bankk = "Unavailable"
                        
                    cc_info = scheme+type+brand
                    if cc_info == "":
                        cc_data = "Unavailable"
                    else:
                        cc_data = cc_info
                    
                    card_send_formatted = f"<b>❆═══»<b>elexa ꜱᴄʀᴀᴘᴇʀ</b>«═══❆</b>\n✮<b>ᴄᴀʀᴅ -» </b><code>{x}</code>\n-———-»<b>ɪɴꜰᴏ</b>«-———-\n✮<b>ʙɪɴ -» </b><code>{bin_1}</code>\n✮<b>ᴅᴀᴛᴀ -» </b>{cc_data}\n✮<b>ʙᴀɴᴋ -» </b>{bankk}\n✮<b>ᴄᴏᴜɴᴛʀʏ -» </b>{country_bin} {country_flag}\n<b>❆═══»<b>elexa ꜱᴄʀᴀᴘᴇʀ</b>«═══❆</b>\n✮<b>ᴏᴡɴᴇʀ -» </b>@hydraCarder605"
                    await bot.send_message(chat_id, text=card_send_formatted)
                    
                else:
                    try:
                        req = requests.get("https://adyen-enc-and-bin-info.herokuapp.com/bin/" + bin_1)
                        jsontext = json.loads(req.text)
                        c_name = jsontext['country']
                        country_flag = " "
                        country_bin = country_codes[c_name]
                        card_send_formatted = "<b>CC - </b><code>{}</code>\n<b>Country -</b> <b>{}</b> {}\n<b>--Group Owner-- -</b> @hydraCarder605\n<b>--Dm to buy non sk checker--</b> - @hydraCarder605".format(x,country_bin,country_flag)
                        await bot.send_message(chat_id, text=card_send_formatted)
                    except:
                        country_bin = "Unavailable"
                        country_flag = " "
                        card_send_formatted = "<b>CC - </b><code>{}</code>\n<b>Country -</b> <b>{}</b> {}\n<b>--Group Owner-- -</b> @hydraCarder605\n<b>--Dm to buy non sk checker--</b> - @hydraCarder605".format(x,country_bin,country_flag)
                        await bot.send_message(chat_id, text=card_send_formatted)
                
            except Exception as e:
                print(f"Error processing bin info: {e}")
                card_send_formatted = "<code>{}</code>".format(x)
                await bot.send_message(chat_id, text=card_send_formatted)
                
    except Exception as e:
        print(f"Error in raw handler: {e}")
        pass

print("Sucessfully Deployed Bot")
bot.start()
app.run()
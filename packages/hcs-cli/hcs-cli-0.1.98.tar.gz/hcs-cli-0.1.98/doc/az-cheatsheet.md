

az account set --subscription a2ef2de8-f2b5-43da-bf68-2b182dd5f928
az account show

az ad group create --display-name titan-lite-customer1 --mail-nickname titan-lite-customer1

az ad user create --display-name titanlitec1u1 --password Hellomortal1! --user-principal-name titanlitec1u1@titanadds.onmicrosoft.com
az ad user show --id titanlitec1u1@titanadds.onmicrosoft.com
az ad group member add --group titan-lite-customer1 --member-id 9a321926-4b03-46f0-a19e-99928adf37ae
az ad group member list --group titan-lite-customer1

az ad user delete --id titanlitec1u1@titanadds.onmicrosoft.com
az ad group delete --group titan-lite-customer1
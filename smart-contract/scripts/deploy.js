const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying BlueCarbonCredit contract to Polygon Amoy...");

  // Get the contract factory
  const BlueCarbonCredit = await hre.ethers.getContractFactory(
    "BlueCarbonCredit"
  );

  // Deploy the contract
  const contract = await BlueCarbonCredit.deploy();
  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();
  console.log("✅ BlueCarbonCredit deployed to:", contractAddress);

  // Get signer information
  const [deployer] = await hre.ethers.getSigners();
  console.log("📍 Deployed by:", deployer.address);

  // Get backend wallet from environment
  const backendWallet =
    process.env.BACKEND_WALLET || "0x0000000000000000000000000000000000000000";

  if (backendWallet !== "0x0000000000000000000000000000000000000000") {
    // Grant MINTER_ROLE to backend wallet
    console.log(`\n🔑 Granting MINTER_ROLE to backend wallet: ${backendWallet}`);
    const MINTER_ROLE = await contract.MINTER_ROLE();
    const tx = await contract.grantRole(MINTER_ROLE, backendWallet);
    await tx.wait();
    console.log("✅ MINTER_ROLE granted");

    // Grant VERIFIER_ROLE to verifier wallet if provided
    const verifierWallet = process.env.VERIFIER_WALLET;
    if (verifierWallet) {
      console.log(
        `\n🔍 Granting VERIFIER_ROLE to verifier wallet: ${verifierWallet}`
      );
      const VERIFIER_ROLE = await contract.VERIFIER_ROLE();
      const tx2 = await contract.grantRole(VERIFIER_ROLE, verifierWallet);
      await tx2.wait();
      console.log("✅ VERIFIER_ROLE granted");
    }
  } else {
    console.log(
      "\n⚠️  BACKEND_WALLET not set in .env. Please grant MINTER_ROLE manually."
    );
  }

  // Save contract info to file
  const fs = require("fs");
  const deploymentInfo = {
    contractAddress,
    deployerAddress: deployer.address,
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId,
    timestamp: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber(),
  };

  fs.writeFileSync(
    "./deployment-info.json",
    JSON.stringify(deploymentInfo, null, 2)
  );
  console.log("\n📄 Deployment info saved to deployment-info.json");

  return contractAddress;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });        